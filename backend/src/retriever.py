# ChromaDB connection extracted
## General 10x Genomics platform knowledge base retriever
import os

import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
COLLECTION_NAME = "platform_docs"


def get_vectorstore() -> Chroma:
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)


def get_retriever(k: int = 4):
    return get_vectorstore().as_retriever(search_kwargs={"k": k})