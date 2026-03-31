"""NLP engine: preprocessing, embeddings, emotion, topic modeling, TurboQuant."""

from human_condition.nlp.preprocessor import (
    clean_text,
    chunk_text,
    preprocess_documents,
)
from human_condition.nlp.turboquant_demo import TurboQuantDemo, QuantizationResult

__all__ = [
    "clean_text",
    "chunk_text",
    "preprocess_documents",
    "Embedder",
    "EmotionClassifier",
    "emotions_to_documents",
    "TurboQuantDemo",
    "QuantizationResult",
]


def __getattr__(name: str):
    """Lazy-load heavy modules to avoid model downloads at import time."""
    if name == "Embedder":
        from human_condition.nlp.embedder import Embedder as _E
        return _E
    if name == "EmotionClassifier":
        from human_condition.nlp.emotion import EmotionClassifier as _EC
        return _EC
    if name == "emotions_to_documents":
        from human_condition.nlp.emotion import emotions_to_documents as _ed
        return _ed
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
