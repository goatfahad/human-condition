"""Chart integration tests — verify all 10 charts produce valid Plotly figures.

All data is fully synthetic — no external API calls, no ML model loading.
Tests complete in under 5 seconds.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import pytest

from human_condition.viz.charts import (
    compression_curve,
    emotion_heatmap,
    emotion_timeline_chart,
    radar_chart,
    similarity_matrix,
    source_distribution,
    summary_stats,
    topic_barchart,
    topic_scatter,
    word_cloud_data,
)


@pytest.fixture
def sample_emotion_data() -> list[dict]:
    """Synthetic emotion data for chart tests."""
    return [
        {"source": "constitution", "joy": 0.4, "sadness": 0.1, "admiration": 0.5},
        {"source": "plato", "curiosity": 0.6, "confusion": 0.2, "admiration": 0.2},
        {"source": "nietzsche", "sadness": 0.5, "grief": 0.3, "remorse": 0.1},
        {"source": "confucius", "admiration": 0.3, "approval": 0.4, "joy": 0.3},
    ]


@pytest.fixture
def sample_benchmark() -> list[dict]:
    """Synthetic TurboQuant benchmark data."""
    return [
        {"compression_ratio": 32.0, "recall_at_10": 0.05, "inner_product_mse": 0.5},
        {"compression_ratio": 16.0, "recall_at_10": 0.15, "inner_product_mse": 0.25},
        {"compression_ratio": 8.0, "recall_at_10": 0.40, "inner_product_mse": 0.10},
        {"compression_ratio": 4.0, "recall_at_10": 0.70, "inner_product_mse": 0.02},
        {"compression_ratio": 2.0, "recall_at_10": 0.90, "inner_product_mse": 0.005},
        {"compression_ratio": 1.0, "recall_at_10": 0.99, "inner_product_mse": 0.001},
    ]


@pytest.fixture
def sample_corpus_dict() -> list[dict]:
    """Sample corpus as dicts."""
    return [
        {"source": "constitution", "title": "US Constitution", "text": "We the people " * 50},
        {"source": "plato", "title": "The Republic", "text": "The cave allegory " * 50},
        {"source": "nietzsche", "title": "Zarathustra", "text": "God is dead " * 50},
        {"source": "confucius", "title": "Analects", "text": "The Master said " * 40},
    ]


# ── Chart Tests ────────────────────────────────────────────────────


class TestEmotionCharts:
    def test_emotion_heatmap(self, sample_emotion_data: list[dict]) -> None:
        fig = emotion_heatmap(sample_emotion_data)
        assert isinstance(fig, go.Figure)

    def test_emotion_timeline(self, sample_emotion_data: list[dict]) -> None:
        fig = emotion_timeline_chart(sample_emotion_data)
        assert isinstance(fig, go.Figure)

    def test_radar_chart(self) -> None:
        profiles = {
            "sacred": {"joy": 0.3, "fear": 0.5, "admiration": 0.4},
            "political": {"anger": 0.2, "approval": 0.6, "sadness": 0.1},
            "philosophical": {"curiosity": 0.7, "confusion": 0.3, "admiration": 0.5},
        }
        fig = radar_chart(profiles)
        assert isinstance(fig, go.Figure)


class TestTopicCharts:
    def test_topic_barchart(self) -> None:
        topics = [
            {"Topic": 0, "Name": "0_justice_law_rights", "Count": 15},
            {"Topic": 1, "Name": "1_philosophy_knowledge", "Count": 12},
            {"Topic": 2, "Name": "2_ethics_virtue_morality", "Count": 10},
            {"Topic": -1, "Name": "-1_noise", "Count": 5},
        ]
        fig = topic_barchart(topics)
        assert isinstance(fig, go.Figure)

    def test_topic_scatter(self) -> None:
        rng = np.random.RandomState(42)
        emb_2d = rng.randn(50, 2)
        labels = list(np.random.randint(0, 5, size=50))
        fig = topic_scatter(emb_2d, labels)
        assert isinstance(fig, go.Figure)


class TestSimilarityCharts:
    def test_similarity_matrix(self) -> None:
        sim = np.array([
            [1.0, 0.7, 0.3],
            [0.7, 1.0, 0.5],
            [0.3, 0.5, 1.0],
        ])
        fig = similarity_matrix(sim, ["constitution", "plato", "nietzsche"])
        assert isinstance(fig, go.Figure)


class TestCorpusCharts:
    def test_source_distribution(self, sample_corpus_dict: list[dict]) -> None:
        fig = source_distribution(sample_corpus_dict)
        assert isinstance(fig, go.Figure)

    def test_word_cloud(self) -> None:
        vocab = [{"word": w, "count": c} for w, c in [
            ("the", 100), ("and", 50), ("of", 40), ("in", 30), ("to", 25),
        ]]
        fig = word_cloud_data(vocab)
        assert isinstance(fig, go.Figure)

    def test_summary_stats(self) -> None:
        stats = [
            {"source": "constitution", "word_count": 350, "dominant_emotion_score": 0.4, "topic": 0, "text": ""},
            {"source": "plato", "word_count": 400, "dominant_emotion_score": 0.3, "topic": 1, "text": ""},
            {"source": "nietzsche", "word_count": 280, "dominant_emotion_score": 0.2, "topic": 2, "text": ""},
        ]
        fig = summary_stats(stats)
        assert isinstance(fig, go.Figure)


class TestTurboQuantCharts:
    def test_compression_curve(self, sample_benchmark: list[dict]) -> None:
        fig = compression_curve(sample_benchmark)
        assert isinstance(fig, go.Figure)

    def test_compression_curve_empty(self) -> None:
        fig = compression_curve([])
        assert isinstance(fig, go.Figure)


class TestEdgeCases:
    """Charts must handle empty/edge-case inputs gracefully."""

    def test_emotion_heatmap_empty(self) -> None:
        fig = emotion_heatmap([])
        assert isinstance(fig, go.Figure)

    def test_topic_barchart_empty(self) -> None:
        fig = topic_barchart([])
        assert isinstance(fig, go.Figure)

    def test_similarity_matrix_small(self) -> None:
        sim = np.array([[1.0]])
        fig = similarity_matrix(sim, ["single"])
        assert isinstance(fig, go.Figure)

    def test_radar_chart_empty(self) -> None:
        fig = radar_chart({})
        assert isinstance(fig, go.Figure)

    def test_summary_stats_empty(self) -> None:
        fig = summary_stats([])
        assert isinstance(fig, go.Figure)

    def test_word_cloud_empty(self) -> None:
        fig = word_cloud_data([])
        assert isinstance(fig, go.Figure)
