import argparse
import os
import tempfile
from pathlib import Path

import boto3
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
COLLECTION_NAME = "platform_docs"


# Load a single file, tagging it with which platform it belongs to
def load_file(path: Path, platform: str):
    if path.suffix.lower() == ".pdf":
        docs = PyPDFLoader(str(path)).load()
    elif path.suffix.lower() == ".txt":
        docs = TextLoader(str(path), encoding="utf-8").load()
    else:
        return []
    for d in docs:
        d.metadata["source_file"] = path.name
        d.metadata["platform"] = platform
    return docs


# Local mode: one subfolder per platform, e.g. docs_staging/xenium/*.pdf
def load_from_local_dir(docs_dir: str):
    all_docs = []
    root = Path(docs_dir)
    for platform_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        platform = platform_dir.name
        for file_path in sorted(platform_dir.iterdir()):
            all_docs.extend(load_file(file_path, platform))
    return all_docs


# S3 mode: same convention, s3://bucket/raw/<platform>/file.pdf
def load_from_s3(bucket: str, prefix: str = "raw/"):
    s3 = boto3.client("s3")
    all_docs = []
    with tempfile.TemporaryDirectory() as tmp:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                relative = key[len(prefix):]
                parts = relative.split("/")
                if len(parts) < 2:
                    continue  # skip anything not organized under a platform folder
                platform = parts[0]
                filename = parts[-1]
                local_path = Path(tmp) / filename
                s3.download_file(bucket, key, str(local_path))
                all_docs.extend(load_file(local_path, platform))
    return all_docs


# Chunk documents into smaller pieces (unchanged from Module 2)
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(docs)


# Embedding and storing the documents in ChromaDB (unchanged from Module 2)
def embed_and_store(chunks, batch_size: int = 100):
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)

    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        vectorstore.add_documents(batch)
        print(f"Embedded and stored {min(i + batch_size, total)}/{total} chunks...")

    print(f"Stored {total} chunks in ChromaDB collection '{COLLECTION_NAME}'")


# Runnable entry point -- now supports EITHER --docs-dir OR --bucket, not both
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--docs-dir")
    group.add_argument("--bucket")
    parser.add_argument("--prefix", default="raw/")
    args = parser.parse_args()

    if args.docs_dir:
        docs = load_from_local_dir(args.docs_dir)
        print(f"Loaded {len(docs)} source document(s) from {args.docs_dir}")
    else:
        docs = load_from_s3(args.bucket, args.prefix)
        print(f"Loaded {len(docs)} source document(s) from s3://{args.bucket}/{args.prefix}")

    if not docs:
        print("No documents found -- nothing to ingest.")
    else:
        chunks = chunk_documents(docs)
        embed_and_store(chunks)