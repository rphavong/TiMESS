import os

import chromadb
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_ollama import OllamaEmbeddings, OllamaLLM

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
COLLECTION_NAME = "platform_docs"

# Prompt template for the LLM to generate a response based on the retrieved context and user query
PROMPT_TEMPLATE = """
You are TiMESS, an expert Field Applications Scientist specializing
in single-cell and spatial biology, with deep knowledge of the 10x
Genomics platform lineup: Flex, Universal, Visium HD, Visium HD 3',
Xenium v1, and Xenium Prime.

Answer the question using ONLY the following context. If the context
does not contain the answer, say the information isn't available in
your current documentation rather than guessing.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

# Helper function to turn retrieved chunks into one text block 
def format_docs(docs) -> str:
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# main function - retriever smoke test first for initial ingest.py validation
def main():
    print("Connecting to ChromaDB and Ollama...")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    db = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 4})

    print("\n--- Testing the retriever ---")
    test_question = "What is the resolution of Xenium?"
    retrieved_docs = retriever.invoke(test_question)
    print(f"Retriever found {len(retrieved_docs)} documents.")

    if not retrieved_docs:
        raise ValueError(
            "The retriever returned no documents. Did "
            "ingest.py run successfully?"
        )

    print("Top result preview:")
    print(retrieved_docs[0].page_content[:400])
    print("-" * 25)

# chain 
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = OllamaLLM(model=OLLAMA_MODEL)
    answer_chain = prompt | llm | StrOutputParser()

    rag_chain = (
        RunnableParallel(
            source_documents=retriever,
            question=RunnablePassthrough(),
        )
        .assign(context=RunnableLambda(lambda x: format_docs(x["source_documents"])))
        .assign(
            answer=RunnableLambda(lambda x: {"context": x["context"], "question": x["question"]})
            | answer_chain
        )
    )

    # Interactive loop for user input
    print("\nTiMESS is ready. Ask a question, or type 'exit' to quit.")

    while True:
        user_question = input("\nYour question: ")
        if user_question.lower() == "exit":
            break

        response = rag_chain.invoke(user_question)

        print("\n--- Sources ---")
        for i, doc in enumerate(response["source_documents"]):
            source = doc.metadata.get("source_file", "N/A")
            print(f"{i + 1}. Source: {source}")
            print(f"   Preview: {doc.page_content[:200]}...")

        print("\nAnswer:")
        print(response["answer"])


if __name__ == "__main__":
    main()