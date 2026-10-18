from fastembed import TextEmbedding

_model = None


def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [vec.tolist() for vec in get_model().embed(texts)]


def embed_query(query: str) -> list[float]:
    return next(iter(get_model().query_embed(query))).tolist()