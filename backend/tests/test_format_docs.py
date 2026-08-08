"""
test_format_docs.py
--------------------
A true unit test -- no ChromaDB, no Ollama, no network calls at all.
This is what CI's "not integration" filter actually needed:
test_retriever.py and test_chain_output.py are BOTH marked
@pytest.mark.integration (correctly -- they need the live stack), so
CI was excluding every single test it had and failing with
"no tests collected" (pytest exit code 5). This test exists purely
to sit on the other side of that filter.

Checks the pure logic in format_docs() from src/chains.py: given a
list of retrieved document chunks, does it join them into one text
block correctly, with a separator between sources?
"""
from langchain_core.documents import Document

from src.chains import format_docs


def test_format_docs_joins_multiple_chunks():
    docs = [
        Document(page_content="Xenium supports FFPE tissue."),
        Document(page_content="Visium HD uses a continuous capture grid."),
    ]

    result = format_docs(docs)

    assert "Xenium supports FFPE tissue." in result
    assert "Visium HD uses a continuous capture grid." in result
    assert "---" in result  # the separator between chunks


def test_format_docs_handles_single_chunk():
    docs = [Document(page_content="Flex uses a fixed probe panel.")]
    assert format_docs(docs) == "Flex uses a fixed probe panel."