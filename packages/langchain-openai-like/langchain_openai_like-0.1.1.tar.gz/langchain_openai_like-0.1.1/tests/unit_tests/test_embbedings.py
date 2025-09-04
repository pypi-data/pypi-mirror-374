from langchain_openai_like import init_openai_like_embeddings


def test_init() -> None:
    emb = init_openai_like_embeddings(model="text-embedding-v4", provider="dashscope")
    assert emb is not None
