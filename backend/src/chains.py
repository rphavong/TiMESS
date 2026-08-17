# LangChain Expression Language - Pull memory into the chain  
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.memory import get_user_memories, save_turn_to_memory
from src.platforms import detect_platforms
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
answer_chain = prompt | llm | StrOutputParser()


def format_docs(docs) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


def retrieve_context(question: str, k: int = 6):
    """
    Any recognized platform mention is treated as at least a
    single-platform-scoped question -- and the curated comparisons
    reference is ALWAYS searched alongside the named platform(s),
    since it's exactly the source built to answer "how does X
    compare to Y" and "what's the headline spec" questions. This
    used to only happen when NO platform was detected at all, which
    excluded it from the exact questions it exists for.
    """
    platforms = detect_platforms(question)

    if not platforms:
        retriever = get_retriever(k=k)
        return retriever.invoke(question), platforms

    search_targets = platforms + ["comparisons"]
    per_target_k = max(2, k // len(search_targets))
    docs = []
    for target in search_targets:
        retriever = get_retriever(k=per_target_k, platform_filter=[target])
        docs.extend(retriever.invoke(question))
    return docs, platforms


def ask(question: str, user_id: str) -> str:
    docs, platforms = retrieve_context(question)
    context = format_docs(docs)
    user_memory = get_user_memories(user_id, question)

    answer = answer_chain.invoke({
        "context": context,
        "question": question,
        "user_memory": user_memory,
    })

    save_turn_to_memory(user_id, question, answer)
    return answer