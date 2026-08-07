import argparse
import os
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
COLLECTION_NAME = "platform_docs"

# load documents from a file
def load_documents(docs_dir: str):
    docs = []
    for path in Path(docs_dir).iterdir():
        if path.suffix.lower() == ".pdf":
            loaded = PyPDFLoader(str(path)).load()
        elif path.suffix.lower() == ".txt":
            loaded = TextLoader(str(path), encoding="utf-8").load()
        else:
            continue
        for d in loaded:
            d.metadata["source_file"] = path.name
        docs.extend(loaded)
    return docs

# Chunk documents into smaller pieces
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_documents(docs)

# Embedding and storing the documents in ChromaDB
def embed_and_store(chunks):
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)        # connects to the ChromaDB server running in a Docker container
    vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)
    vectorstore.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'")

# Runnable entry point for the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", default="scripts/sample_docs")
    args = parser.parse_args()

    docs = load_documents(args.docs_dir)
    print(f"Loaded {len(docs)} source document(s) from {args.docs_dir}")

    if not docs:
        print("No .pdf or .txt files found -- add some and try again.")
    else:
        chunks = chunk_documents(docs)
        embed_and_store(chunks)