"""Sentence embedding module using sentence-transformers."""
from __future__ import annotations

import numpy as np
from pathlib import Path


def _get_SentenceTransformer():
    """Lazy-load to avoid model download at import time."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer


def _get_torch():
    """Lazy-load torch."""
    import torch
    return torch


class Embedder:
    """Wraps a sentence-transformers model for text embedding.

    Auto-detects device priority: CUDA > MPS > CPU.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        cache_dir: str | None = None,
    ) -> None:
        self.model_name = model_name
        if device is None:
            self.device = _auto_detect_device()
        else:
            self.device = device
        ST = _get_SentenceTransformer()
        self.model = ST(
            model_name,
            device=self.device,
            cache_folder=cache_dir,
        )

    def embed_texts(
        self,
        texts: list[str],
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> np.ndarray:
        """Generate normalized L2 embeddings for a list of strings.

        Returns:
            np.ndarray of shape (n_texts, embedding_dim), L2-normalized
        """
        if not texts:
            raise ValueError("texts must not be empty")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        result: np.ndarray = embeddings
        return result

    def embed_documents(
        self, docs: list, batch_size: int = 32
    ) -> tuple[np.ndarray, list[str]]:
        """Extract text from Documents, embed, return embeddings + texts."""
        texts = [d.text for d in docs]
        embeddings = self.embed_texts(texts, batch_size=batch_size)
        return embeddings, texts

    def save_embeddings(self, path: Path | str, embeddings: np.ndarray) -> None:
        """Save embeddings array to disk as .npy."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(str(path), embeddings)

    def load_embeddings(self, path: Path | str) -> np.ndarray:
        """Load embeddings array from .npy file."""
        result: np.ndarray = np.load(str(path))
        return result

    @property
    def embedding_dim(self) -> int:
        dim = self.model.get_sentence_embedding_dimension()
        assert dim is not None
        result: int = int(dim)
        return result


def _auto_detect_device() -> str:
    """Detect available compute device. Priority: cuda > mps > cpu."""
    torch = _get_torch()
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
