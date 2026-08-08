# LangChain Expression Language - Pull memory into the chain  
import os
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.memory import get_user_memories, save_turn_to_memory
from src.retriever import get_retriever

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

SYSTEM_PROMPT = """You are TiMESS, an expert Field Applications \
Scientist specializing in single-cell and spatial biology, with deep \
knowledge of the 10x Genomics platform lineup: Flex, Universal, \
Visium HD, Visium HD 3', Xenium v1, and Xenium Prime.

Answer using ONLY the reference documentation and user context \
provided below. If the documentation doesn't cover the question, say \
so honestly rather than guessing.

Reference documentation:
{context}

What you know about this user from previous conversations:
{user_memory}
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "{question}")]
)

llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)


def format_docs(docs) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


def build_chain():
    retriever = get_retriever()
    return (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "user_memory": itemgetter("user_memory"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )


_chain = None


def get_chain():
    global _chain
    if _chain is None:
        _chain = build_chain()
    return _chain


def ask(question: str, user_id: str) -> str:
    """
    The single function the API layer (Module 5) calls. This is the
    "public interface" of the whole RAG + memory system -- callers
    don't need to know ChromaDB, Mem0, or Ollama exist underneath.
    """
    user_memory = get_user_memories(user_id, question)
    chain = get_chain()
    answer = chain.invoke({"question": question, "user_memory": user_memory})
    save_turn_to_memory(user_id, question, answer)
    return answer