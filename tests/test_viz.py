"""Tests for viz module: theme, charts."""
from __future__ import annotations

import numpy as np
import pytest

from human_condition.viz.theme import (
    ACCENT_GOLD,
    BG_PRIMARY,
    PALETTE,
)
from human_condition.viz.charts import (
    apply_theme,
    emotion_heatmap,
    topic_scatter,
    similarity_matrix,
    compression_curve,
    source_distribution,
    emotion_timeline_chart,
    topic_barchart,
    word_cloud_data,
    radar_chart,
    summary_stats,
)
from human_condition.corpus.document import Document


# ── Theme Tests ────────────────────────────────────────────────────


def test_theme_constants_are_defined():
    assert isinstance(ACCENT_GOLD, str)
    assert isinstance(BG_PRIMARY, str)
    assert len(PALETTE) > 5


def test_apply_theme_sets_title():
    import plotly.graph_objects as go
    fig = go.Figure()
    result = apply_theme(fig, "Test Title")
    assert result.layout.title.text == "Test Title"


def test_apply_theme_returns_figure():
    import plotly.graph_objects as go
    fig = go.Figure()
    result = apply_theme(fig, "Title")
    assert result is not None


# ── Synthetic Fixtures ─────────────────────────────────────────────


@pytest.fixture
def sample_emotion_data():
    return [
        {"source": "plato", "admiration": 0.3, "fear": 0.7, "joy": 0.1, "sadness": 0.2},
        {"source": "quran", "admiration": 0.5, "fear": 0.2, "joy": 0.4, "sadness": 0.1},
        {"source": "marx", "admiration": 0.1, "fear": 0.8, "joy": 0.05, "sadness": 0.6},
    ]


@pytest.fixture
def sample_docs():
    return [
        Document(source="plato", title="Republic", text="Short text content here " * 10),
        Document(source="quran", title="Fatiha", text="Another text block here " * 8),
        Document(source="marx", title="Manifesto", text="Words words words " * 15),
        Document(source="plato", title="Phaedo", text="Plato text example " * 5),
    ]


# ── Chart Tests ───────────────────────────────────────────────────


def test_emotion_heatmap_returns_figure(sample_emotion_data):
    fig = emotion_heatmap(sample_emotion_data)
    assert hasattr(fig, "data")


def test_source_distribution_returns_figure(sample_docs):
    fig = source_distribution(sample_docs)
    assert hasattr(fig, "data")
    assert len(fig.data) > 0


def test_similarity_matrix_returns_figure():
    sim = np.array([[1.0, 0.5], [0.5, 1.0]])
    fig = similarity_matrix(sim, ["Source A", "Source B"])
    assert hasattr(fig, "data")


def test_compression_curve_returns_figure():
    data = [
        {"bits": 32.0, "compressed_bits_per_channel": 32.0, "recall_at_10": 1.0, "inner_product_mse": 0.0, "compression_ratio": 1.0},
        {"bits": 32.0, "compressed_bits_per_channel": 4.0, "recall_at_10": 0.95, "inner_product_mse": 0.01, "compression_ratio": 8.0},
        {"bits": 32.0, "compressed_bits_per_channel": 2.0, "recall_at_10": 0.8, "inner_product_mse": 0.1, "compression_ratio": 16.0},
    ]
    fig = compression_curve(data)
    assert hasattr(fig, "data")


def test_compression_curve_empty():
    fig = compression_curve([])
    assert hasattr(fig, "data")


def test_topic_barchart_returns_figure():
    info = [
        {"Topic": 0, "Count": 50, "Name": "Philosophy"},
        {"Topic": 1, "Count": 30, "Name": "Religion"},
        {"Topic": 2, "Count": 20, "Name": "Politics"},
    ]
    fig = topic_barchart(info)
    assert hasattr(fig, "data")


def test_topic_barchart_empty():
    fig = topic_barchart([])
    assert hasattr(fig, "data")


def test_radar_chart_returns_figure():
    profiles = {
        "sacred": {"joy": 0.5, "fear": 0.3, "admiration": 0.7},
        "political": {"joy": 0.2, "fear": 0.6, "admiration": 0.1},
    }
    fig = radar_chart(profiles)
    assert hasattr(fig, "data")


def test_radar_chart_empty():
    fig = radar_chart({})
    assert hasattr(fig, "data")


def test_summary_stats_returns_figure():
    stats = [
        {"word_count": 100, "source": "plato", "dominant_emotion_score": 0.5, "topic": 0, "text": "text"},
        {"word_count": 150, "source": "quran", "dominant_emotion_score": 0.3, "topic": 0, "text": "text"},
        {"word_count": 80, "source": "marx", "dominant_emotion_score": 0.7, "topic": 1, "text": "text"},
    ]
    fig = summary_stats(stats)
    assert hasattr(fig, "data")


def test_emotion_timeline_returns_figure(sample_emotion_data):
    fig = emotion_timeline_chart(sample_emotion_data)
    assert hasattr(fig, "data")


def test_word_cloud_returns_figure():
    vocab = [
        {"word": "justice", "count": 50},
        {"word": "love", "count": 40},
        {"word": "power", "count": 30},
    ]
    fig = word_cloud_data(vocab)
    assert hasattr(fig, "data")


def test_topic_scatter_returns_figure():
    emb_2d = np.random.randn(20, 2)
    labels = [0] * 10 + [1] * 10
    fig = topic_scatter(emb_2d, [str(l) for l in labels])
    assert hasattr(fig, "data")


def test_topic_scatter_empty():
    emb_2d = np.array([]).reshape(0, 2)
    fig = topic_scatter(emb_2d, [])
    assert hasattr(fig, "data")


def test_word_cloud_empty():
    fig = word_cloud_data([])
    assert hasattr(fig, "data")


def test_summary_stats_empty():
    fig = summary_stats([])
    assert hasattr(fig, "data")


def test_emotion_timeline_empty():
    fig = emotion_timeline_chart([])
    assert hasattr(fig, "data")