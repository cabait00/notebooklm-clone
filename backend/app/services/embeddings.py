from app.config import settings

_model = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()


def _get_model():
    global _model
    if _model is None:
        # Lazy import — keeps module import fast and avoids loading torch in tests
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model)
    return _model
