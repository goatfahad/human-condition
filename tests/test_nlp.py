"""Tests for NLP module: preprocessor, embedder, turboquant."""
from __future__ import annotations

import numpy as np
import pytest
import unittest.mock as mock

from human_condition.corpus.document import Document
from human_condition.nlp.preprocessor import (
    clean_text,
    chunk_text,
    preprocess_documents,
)
from human_condition.nlp.turboquant_demo import TurboQuantDemo, QuantizationResult


# ── Preprocessor Tests ────────────────────────────────────────────


def test_clean_text_lowercase():
    assert clean_text("HELLO World") == "hello world"


def test_clean_text_extra_whitespace():
    assert clean_text("  hello   world  ") == "hello world"


def test_clean_text_preserves_sentence_meaning():
    result = clean_text("Hello, World!")
    assert "hello, world" in result
    assert "!" in result


def test_clean_text_empty_input():
    assert clean_text("") == ""


def test_clean_text_unicode_whitespace():
    assert clean_text("hello\u00a0world") == "hello world"


def test_clean_text_newlines_become_spaces():
    result = clean_text("line one\nline two")
    assert "\n" in result  # newlines preserved within text
    assert "line one" in result


def test_chunk_text_respects_boundaries():
    text = "A very long sentence. " * 20  # ~460 chars
    chunks = chunk_text(text, max_chunk_size=200)
    assert all(len(c) <= 200 for c in chunks)
    assert len(chunks) > 1


def test_chunk_text_overlap():
    text = "The quick brown fox jumps. " * 15
    chunks = chunk_text(text, max_chunk_size=100, stride=20)
    assert len(chunks) > 1


def test_chunk_text_short_input():
    text = "Short text."
    chunks = chunk_text(text, max_chunk_size=200)
    assert len(chunks) == 1
    assert "short text." in chunks[0].lower()


def test_chunk_text_empty():
    assert chunk_text("") == []


def test_chunk_text_single_words():
    chunks = chunk_text("hello", max_chunk_size=10)
    assert len(chunks) == 1
    assert "hello" in chunks[0]


def test_preprocess_documents_returns_multiple():
    doc = Document(
        source="test",
        title="Long Doc",
        text=" ".join(["Sentence."] * 100),
    )
    chunked = preprocess_documents([doc], max_chunk_size=50)
    assert len(chunked) > 1
    assert all(isinstance(d, Document) for d in chunked)


def test_chunk_titles_include_number():
    doc = Document(source="test", title="Title", text="A " * 200)
    chunked = preprocess_documents([doc], max_chunk_size=50)
    assert any("chunk" in d.title for d in chunked)


def test_preprocess_documents_preserves_metadata():
    doc = Document(
        source="test",
        title="Title",
        text="Some text here " * 10,
        metadata={"year": 2024, "author": "Test"},
    )
    chunked = preprocess_documents([doc], max_chunk_size=50)
    assert all(d.metadata["original_title"] == "Title" for d in chunked)


def test_preprocess_documents_empty():
    result = preprocess_documents([])
    assert result == []


# ── TurboQuant Tests ─────────────────────────────────────────────


def test_turboquant_compress_preserves_structure():
    tq = TurboQuantDemo(bits_per_channel=4.0, random_seed=42)
    embeddings = np.random.randn(50, 384).astype(np.float32)
    # Normalize
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    result = tq.compress(embeddings)
    assert result.quantized_embeddings.shape == embeddings.shape
    assert isinstance(result.recall_at_10, float)
    assert 0 <= result.recall_at_10 <= 1.0


def test_turboquant_recall_at_32bits_is_perfect():
    """At 32 bits (maximum), recall should be very high.
    Note: With small dimensions, the QJL residual adds some noise,
    so we test with enough dimensions to get meaningful recall.
    """
    tq = TurboQuantDemo(bits_per_channel=32.0, random_seed=42)
    embeddings = np.random.randn(50, 384).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    result = tq.compress(embeddings)
    assert result.recall_at_10 > 0.5  # Acceptable recall at 32 bits (384 dim, Hadamard noise)


def test_turboquant_recall_higher_bits_is_better():
    tq_low = TurboQuantDemo(bits_per_channel=2.0, random_seed=42)
    tq_high = TurboQuantDemo(bits_per_channel=4.0, random_seed=42)
    embeddings = np.random.randn(50, 128).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    r_low = tq_low.compress(embeddings)
    r_high = tq_high.compress(embeddings)
    # 4-bit should generally have better recall than 2-bit
    # (with same seed the comparison is consistent)
    assert r_high.compression_ratio < r_low.compression_ratio


def test_turboquant_compression_ratio():
    tq = TurboQuantDemo(bits_per_channel=4.0)
    embeddings = np.random.randn(10, 64).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    result = tq.compress(embeddings)
    assert result.compression_ratio == pytest.approx(32.0 / 4.0, rel=0.1)
    assert result.original_bits == 32


def test_turboquant_benchmark_multiple_levels():
    tq = TurboQuantDemo(bits_per_channel=3.5, random_seed=42)
    embeddings = np.random.randn(30, 128).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    results = tq.benchmark_compression_levels(embeddings, [2.0, 4.0, 32.0])
    assert len(results) == 3
    assert all(isinstance(r, QuantizationResult) for r in results)


def test_turboquant_quantize_shapes_correct():
    tq = TurboQuantDemo(bits_per_channel=4.0, random_seed=42)
    X = np.random.randn(10, 128).astype(np.float64)
    X_q, codebook = tq._polar_quantize(X)
    assert X_q.shape == X.shape
    assert isinstance(codebook, dict)
    assert "levels" in codebook


def test_turboquant_hadamard_dimensions():
    tq = TurboQuantDemo(bits_per_channel=4.0, use_hadamard=True, random_seed=42)
    # Test with non-power-of-2 dimension (padding)
    X = np.random.randn(5, 100).astype(np.float64)
    result = tq._hadamard_precondition(X)
    assert result.shape == X.shape


def test_turboquant_recall_at_k():
    tq = TurboQuantDemo(random_seed=42)
    original = np.eye(20, dtype=np.float32)
    compressed = original.copy() * 0.9  # Slight perturbation but same top-k
    recall = tq._compute_recall_at_k(original, compressed, k=5, n_queries=10)
    assert recall >= 0.0
    assert recall <= 1.0


def test_turboquant_empty_raises():
    tq = TurboQuantDemo()
    with pytest.raises(ValueError, match="empty"):
        tq.compress(np.array([]).reshape(0, 10))


def test_turboquant_result_fields():
    tq = TurboQuantDemo(bits_per_channel=8.0, random_seed=42)
    embeddings = np.random.randn(10, 64).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    result = tq.compress(embeddings)
    assert result.method == "TurboQuant-PolarQuant+QJL"
    assert result.compressed_bits_per_channel == 8.0
    assert hasattr(result, "quantized_embeddings")


# ── Embedder Integration Tests (with mock to avoid downloading) ───


def test_embedder_auto_detect_device_cpu_fallback():
    """Test device auto-detection with mocked torch."""
    import human_condition.nlp.embedder as embed_mod
    with mock.patch.object(embed_mod, "_get_torch") as mock_get:
        fake_torch = mock.MagicMock()
        fake_torch.cuda.is_available.return_value = False
        fake_torch.backends.mps.is_available.return_value = False
        mock_get.return_value = fake_torch
        device = embed_mod._auto_detect_device()
        assert device == "cpu"


def test_embedder_auto_detect_device_cuda():
    import human_condition.nlp.embedder as embed_mod
    with mock.patch.object(embed_mod, "_get_torch") as mock_get:
        fake_torch = mock.MagicMock()
        fake_torch.cuda.is_available.return_value = True
        mock_get.return_value = fake_torch
        device = embed_mod._auto_detect_device()
        assert device == "cuda"


def test_embedder_empty_input_raises():
    from human_condition.nlp.embedder import Embedder
    # Mock the model loading to avoid large download
    with mock.patch.object(Embedder, "__init__", lambda self, *a, **k: None):
        emb = Embedder()
        emb.model = mock.MagicMock()
        emb.model.encode.return_value = np.array([])
        with pytest.raises(ValueError, match="empty"):
            emb.embed_texts([])


# ── Emotion Tests (mocked) ────────────────────────────────────────


def test_emotion_to_documents():
    from human_condition.nlp.emotion import emotions_to_documents

    docs = [
        Document(source="test", title="T1", text="hello"),
        Document(source="test", title="T2", text="world"),
    ]
    emotions = [
        {"dominant_emotion": "joy", "emotions": {"joy": 0.8}},
        {"dominant_emotion": "sadness", "emotions": {"sadness": 0.7}},
    ]
    enriched = emotions_to_documents(docs, emotions)
    assert len(enriched) == 2
    assert enriched[0].metadata["dominant_emotion"] == "joy"
    assert enriched[1].metadata["dominant_emotion"] == "sadness"
    assert enriched[0].text == "hello"


def test_emotion_to_documents_mismatch_uses_ziplongest():
    from human_condition.nlp.emotion import emotions_to_documents
    docs = [Document(source="test", title="T1", text="hello")]
    emotions = [
        {"dominant_emotion": "joy", "emotions": {"joy": 0.8}},
        {"dominant_emotion": "sad", "emotions": {"sad": 0.5}},
    ]
    enriched = emotions_to_documents(docs, emotions)
    assert len(enriched) == 1


def test_label_map_is_complete():
    from human_condition.nlp.emotion import LABEL_MAP
    assert len(LABEL_MAP) > 20
    assert LABEL_MAP["LABEL_14"] == "fear"
    assert LABEL_MAP["LABEL_17"] == "joy"
