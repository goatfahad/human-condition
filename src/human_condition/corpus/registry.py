"""Registry for corpus source loaders — maps source IDs to callables."""
from __future__ import annotations

from collections.abc import Callable

from human_condition.corpus.document import Document

LoaderFn = Callable[[], list[Document]]


class CorpusRegistry:
    """Central mapping of source identifiers to loader functions.

    Each loader is a zero-argument callable that returns a list of Documents.
    Registration and retrieval are separate — sources register themselves
    at import time via side-effects in their module.
    """

    def __init__(self) -> None:
        self._loaders: dict[str, LoaderFn] = {}

    def register(self, source_id: str, loader: LoaderFn) -> None:
        """Register a loader function for a source.

        Raises:
            ValueError: If source_id is already registered.
        """
        if source_id in self._loaders:
            raise ValueError(f"Source '{source_id}' is already registered")
        self._loaders[source_id] = loader

    def load(self, source_id: str) -> list[Document]:
        """Load all documents from a named source.

        Raises:
            KeyError: If source_id is not registered.
        """
        if source_id not in self._loaders:
            raise KeyError(f"Unknown corpus source: '{source_id}'")
        return self._loaders[source_id]()

    def has_source(self, source_id: str) -> bool:
        return source_id in self._loaders

    def list_sources(self) -> list[str]:
        return sorted(self._loaders.keys())
