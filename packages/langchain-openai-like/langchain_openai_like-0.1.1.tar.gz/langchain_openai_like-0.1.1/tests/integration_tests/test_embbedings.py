"""Test OpenAI Like embeddings."""

from langchain_openai_like import init_openai_like_embeddings

embedding = init_openai_like_embeddings(
    model="text-embedding-v4", provider="dashscope", chunk_size=10
)


def test_langchain_openai_embedding_documents() -> None:
    documents = ["foo bar"]

    output = embedding.embed_documents(documents)
    assert len(output) == 1
    assert len(output[0]) > 0


def test_langchain_openai_embedding_query() -> None:
    document = "foo bar"
    output = embedding.embed_query(document)
    assert len(output) > 0


def test_langchain_openai_embeddings_dimensions() -> None:
    embedding = init_openai_like_embeddings(
        model="text-embedding-v4", provider="dashscope", dimensions=128
    )
    documents = ["foo bar"]
    output = embedding.embed_documents(documents)
    assert len(output) == 1
    assert len(output[0]) == 128


def test_langchain_openai_embeddings_dimensions_large_num() -> None:
    documents = [f"foo bar {i}" for i in range(100)]
    output = embedding.embed_documents(documents)
    assert len(output) == 100
    assert len(output[0]) == 1024
