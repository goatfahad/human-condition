"""Tests for Corpus module: Document, Registry, Builder.

All external API calls are mocked so tests complete in <10s.
Real APIs are hit only at runtime during actual pipeline execution.
"""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest
import requests

from human_condition.corpus.document import Document, document_id
from human_condition.corpus.registry import CorpusRegistry
from human_condition.corpus.builder import (
    CorpusBuilder,
    load_constitution,
    load_communist_manifesto,
    load_marx,
    load_plato,
    load_nietzsche,
    load_confucius,
    load_quran,
    load_bible,
    load_gutenberg,
)


# ── Document Tests ──────────────────────────────────────────────────


def test_document_creation():
    doc = Document(
        source="gutenberg",
        title="Alice in Wonderland",
        text="Hello world, this is content.",
        metadata={"year": 1865, "author": "Lewis Carroll"},
    )
    assert doc.source == "gutenberg"
    assert doc.title == "Alice in Wonderland"
    assert doc.text == "Hello world, this is content."
    assert doc.metadata["year"] == 1865


def test_document_computed_id():
    doc = Document(source="quran", title="The Opening", text="In the name of God...")
    assert doc.id.startswith("quran_the_opening")


def test_document_strips_whitespace():
    doc = Document(source="bible", title="  Genesis  ", text="  Some text with padding  ")
    assert doc.title == "Genesis"
    assert doc.text == "Some text with padding"


def test_document_text_can_be_empty():
    doc = Document(source="test", title="Empty", text="")
    assert doc.text == ""


def test_document_metadata_defaults_to_empty_dict():
    doc = Document(source="test", title="No Meta", text="text")
    assert doc.metadata == {}


def test_document_id_function():
    doc_a = Document(source="src", title="Title A", text="hello")
    assert document_id(doc_a) == "src_title_a"


def test_document_id_deduplicates():
    doc_a = Document(source="src", title="Title A", text="hello")
    doc_b = Document(source="src", title="Title A", text="world")
    assert document_id(doc_a) == document_id(doc_b)


def test_document_len():
    doc = Document(source="test", title="Len Test", text="abcde")
    assert len(doc) == 5


def test_document_word_count():
    doc = Document(source="test", title="Word Count", text="one two three")
    assert doc.word_count == 3


def test_document_empty_source_raises():
    with pytest.raises(ValueError, match="source"):
        Document(source="", title="Bad", text="text")


def test_document_empty_title_raises():
    with pytest.raises(ValueError, match="title"):
        Document(source="x", title="  ", text="text")


def test_document_frozen():
    doc = Document(source="test", title="Frozen", text="text")
    with pytest.raises(Exception):  # FrozenInstanceError
        doc.title = "Changed"


def test_document_special_chars_in_id():
    doc = Document(source="reddit", title="What's the point!?", text="text")
    doc_id = document_id(doc)
    assert "reddit" in doc_id
    assert "!" not in doc_id


# ── Registry Tests ──────────────────────────────────────────────────


def test_registry_register_and_load():
    registry = CorpusRegistry()
    registry.register("dummy", lambda: [Document("dummy", "Test", "hello")])
    docs = registry.load("dummy")
    assert len(docs) == 1
    assert docs[0].source == "dummy"


def test_registry_unknown_source_raises():
    registry = CorpusRegistry()
    with pytest.raises(KeyError, match="unknown"):
        registry.load("unknown")


def test_registry_duplicate_registration_raises():
    registry = CorpusRegistry()
    registry.register("x", lambda: [])
    with pytest.raises(ValueError, match="x"):
        registry.register("x", lambda: [])


def test_registry_list_sources():
    registry = CorpusRegistry()
    registry.register("b", lambda: [])
    registry.register("a", lambda: [])
    assert registry.list_sources() == ["a", "b"]


def test_registry_has_source():
    registry = CorpusRegistry()
    registry.register("foo", lambda: [])
    assert registry.has_source("foo") is True
    assert registry.has_source("bar") is False
    assert registry.has_source("FOO") is False


# ── Builder Tests (all hardcoded sources — no network) ──────────────


def test_builder_builds_hardcoded_sources():
    """Test hardcoded loaders only — zero network calls."""
    registry = CorpusRegistry()
    registry.register("constitution", load_constitution)
    registry.register("communist_manifesto", load_communist_manifesto)
    registry.register("marx", load_marx)
    registry.register("plato", load_plato)
    registry.register("nietzsche", load_nietzsche)
    registry.register("confucius", load_confucius)
    builder = CorpusBuilder(registry=registry, auto_register=False)
    docs = builder.build()
    sources = {d.source for d in docs}
    for expected in [
        "constitution", "communist_manifesto", "marx",
        "plato", "nietzsche", "confucius",
    ]:
        assert expected in sources


def test_builder_all_docs_are_documents():
    registry = CorpusRegistry()
    registry.register("constitution", load_constitution)
    registry.register("plato", load_plato)
    builder = CorpusBuilder(registry=registry, auto_register=False)
    docs = builder.build()
    assert isinstance(docs, list)
    assert all(isinstance(d, Document) for d in docs)


def test_hardcoded_sources_have_content():
    """Each hardcoded source has substantial text."""
    for loader in [
        load_constitution, load_communist_manifesto, load_marx,
        load_plato, load_nietzsche, load_confucius,
    ]:
        docs = loader()
        assert len(docs) == 1
        assert len(docs[0].text) > 50, f"{docs[0].title} too short"


# ── Builder Tests API loaders (mocked) ─────────────────────────────


def test_quran_loader_with_mock():
    """Quran loader handles the Quran.com API response correctly."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "chapters": [
            {
                "id": 1,
                "name_simple": "Al-Fatihah",
                "revelation_place": "makkah",
            },
        ]
    }

    def chapter_endpoint(url, **kwargs):
        mock = MagicMock()
        mock.status_code = 200
        if "chapters" in url:
            mock.json.return_value = mock_resp.json()
        elif "verses" in url:
            mock.json.return_value = {
                "verses": [
                    {"translations": [{"text": "In the name of God"}]}
                ]
            }
        return mock

    with patch("human_condition.corpus.builder.requests.get", side_effect=chapter_endpoint):
        docs = load_quran()
        assert len(docs) == 1
        assert docs[0].source == "quran"
        assert docs[0].title == "Al-Fatihah"
        assert "In the name of God" in docs[0].text


def test_quran_loader_api_failure():
    """Quran loader returns fallback document when API fails."""
    with patch("human_condition.corpus.builder.requests.get", side_effect=requests.RequestException("network error")):
        docs = load_quran()
        assert len(docs) == 1
        assert docs[0].source == "quran"
        assert "Failed" in docs[0].text or "error" in docs[0].text.lower()


def test_bible_loader_with_mock():
    """Bible loader handles the bible-api.com response correctly."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "text": "In the beginning God created",
        "reference": "Genesis 1",
    }

    with patch("human_condition.corpus.builder.requests.get", return_value=mock_resp):
        docs = load_bible()
        assert len(docs) > 0
        assert docs[0].source == "bible"


def test_bible_loader_api_failure():
    """Bible loader returns fallback documents when APIs fail."""
    with patch("human_condition.corpus.builder.requests.get", side_effect=requests.RequestException("network")):
        docs = load_bible()
        assert len(docs) > 0
        assert docs[0].source == "bible"
        assert all(isinstance(d, Document) for d in docs)


@pytest.mark.skip(reason="nltk download is slow in test environment")
def test_gutenberg_loader_with_mock():
    """Gutenberg loader uses nltk corpus — mock nltk if available."""
    import nltk as _nltk
    # Mock nltk.corpus.gutenberg to return minimal data
    mock_corpus = MagicMock()
    mock_corpus.fileids.return_value = ["shakespeare-hamlet.txt"]
    mock_corpus.raw.return_value = "To be or not to be, that is the question."
    with patch("human_condition.corpus.builder.nltk.corpus.gutenberg", mock_corpus):
        with patch.object(_nltk, "download"):
            docs = load_gutenberg()
            assert len(docs) == 1
            assert docs[0].source == "gutenberg"


def test_gutenberg_loader_failure():
    """Gutenberg loader raises ImportError if nltk missing."""
    import builtins
    orig_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "nltk":
            raise ImportError("no nltk")
        return orig_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ImportError, match="nltk"):
            load_gutenberg()
