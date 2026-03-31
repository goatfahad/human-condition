"""Ten Plotly charts for The Human Condition dashboard."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from human_condition.viz.theme import (
    BG_PRIMARY,
    BG_SECONDARY,
    BG_CARD,
    ACCENT_GOLD,
    ACCENT_CYAN,
    ACCENT_PINK,
    ACCENT_PURPLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    PALETTE,
    FONT_FAMILY,
    PLOTLY_TEMPLATE,
)


# ── Utility ────────────────────────────────────────────────────────


def apply_theme(fig: go.Figure, title: str) -> go.Figure:
    """Apply dark theme to a Plotly figure."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title={
            "text": title,
            "font": {"color": ACCENT_GOLD, "size": 20, "family": FONT_FAMILY},
            "x": 0.5,
            "xanchor": "center",
        },
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        font={"color": TEXT_PRIMARY, "family": FONT_FAMILY},
        margin={"l": 60, "r": 40, "t": 80, "b": 60},
        xaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
    )
    return fig


def RGBA(r: int, g: int, b: int, a: float) -> str:
    return f"rgba({r},{g},{b},{a})"


def save_chart(fig: go.Figure, filename: str, dir: Path | None = None) -> str:
    """Save chart as HTML file."""
    if dir is None:
        dir = Path(".")
    dir.mkdir(parents=True, exist_ok=True)
    path = dir / filename
    fig.write_html(str(path))
    return str(path)


# ── Chart 1: Emotion Heatmap ───────────────────────────────────────


def emotion_heatmap(emotion_data: list[dict]) -> go.Figure:
    """Heatmap: emotion probability across corpus sources."""
    sources = sorted({d.get("source", "unknown") for d in emotion_data})
    emotion_cols = [
        k for k in emotion_data[0].keys()
        if k not in ("source", "title", "text", "metadata")
    ] if emotion_data else []

    if not emotion_cols or not sources:
        fig = go.Figure()
        return apply_theme(fig, "Emotion Spectrum Across 5,000 Years of Text")

    z = np.zeros((len(sources), len(emotion_cols)))
    for i, src in enumerate(sources):
        src_docs = [d for d in emotion_data if d.get("source") == src]
        for j, col in enumerate(emotion_cols):
            vals = [d.get(col, 0) for d in src_docs if isinstance(d.get(col, 0), (int, float))]
            z[i, j] = np.mean(vals) if vals else 0

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=emotion_cols,
            y=[s.replace("_", " ").title() for s in sources],
            colorscale=[[0, BG_CARD], [0.5, ACCENT_CYAN], [1, ACCENT_GOLD]],
            hoverongaps=False,
        )
    )
    fig.update_layout(
        xaxis={"title": "Emotion", "gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"title": "Source", "gridcolor": RGBA(255, 255, 255, 0.08)},
    )
    return apply_theme(fig, "Emotion Spectrum Across 5,000 Years of Text")


# ── Chart 2: Topic Scatter ────────────────────────────────────────


def topic_scatter(
    embedding_2d: np.ndarray,
    topic_labels: list[str],
) -> go.Figure:
    """2D scatter of topics (from UMAP/PCA) colored by topic."""
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(set(topic_labels)))]
    unique_topics = sorted(set(t for t in topic_labels if t != -1))

    fig = go.Figure()
    for idx, topic in enumerate(unique_topics):
        mask = np.array(topic_labels) == topic
        xs = embedding_2d[mask, 0]
        ys = embedding_2d[mask, 1]
        color = PALETTE[idx % len(PALETTE)]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            name=f"Topic {topic}",
            marker={"color": color, "size": 5, "opacity": 0.7},
            hoverinfo="name",
        ))

    fig.update_layout(
        xaxis={"title": "Dimension 1", "gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"title": "Dimension 2", "gridcolor": RGBA(255, 255, 255, 0.08)},
        showlegend=True,
    )
    return apply_theme(fig, "Semantic Landscape of Human Thought")


# ── Chart 3: Similarity Matrix ─────────────────────────────────────


def similarity_matrix(
    similarity_data: np.ndarray,
    source_names: list[str],
) -> go.Figure:
    """Cross-source document similarity heatmap."""
    n = similarity_data.shape[0]
    names = source_names[:n] if len(source_names) >= n else source_names + [""] * (n - len(source_names))

    fig = go.Figure(
        data=go.Heatmap(
            z=similarity_data,
            x=names,
            y=names,
            colorscale=[[0, BG_CARD], [1, ACCENT_PURPLE]],
            hoverongaps=False,
            zmin=0,
            zmax=1,
        )
    )
    fig.update_layout(
        xaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
    )
    return apply_theme(fig, "Cross-Century Semantic Bridges")


# ── Chart 4: Compression Curve ────────────────────────────────────


def compression_curve(benchmark_results: list[dict]) -> go.Figure:
    """TurboQuant benchmark: compression vs recall.

    benchmark_results: list of dicts with keys:
      - compressed_bits_per_channel / bits
      - recall_at_10
      - inner_product_mse
      - compression_ratio
    """
    if not benchmark_results:
        fig = go.Figure()
        return apply_theme(fig, "TurboQuant: Compression vs Quality")

    ratios = [r.get("compression_ratio", r.get("bits", 32) / r.get("compressed_bits_per_channel", 1))
              for r in benchmark_results]
    recalls = [r.get("recall_at_10", 0) for r in benchmark_results]
    mses = [r.get("inner_product_mse", 0) for r in benchmark_results]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=ratios, y=recalls,
            mode="lines+markers",
            name="Recall@10",
            line={"color": ACCENT_GOLD, "width": 3},
            marker={"size": 8},
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=ratios, y=mses,
            mode="lines+markers",
            name="IP-MSE",
            line={"color": ACCENT_PINK, "width": 2, "dash": "dash"},
            marker={"size": 6},
        ),
        secondary_y=True,
    )
    fig.update_layout(
        xaxis={"title": "Compression Ratio (x)", "gridcolor": RGBA(255, 255, 255, 0.08)},
    )
    fig.update_yaxes(title_text="Recall@10", secondary_y=False, gridcolor=RGBA(255, 255, 255, 0.08))
    fig.update_yaxes(title_text="Inner Product MSE", secondary_y=True, gridcolor=RGBA(255, 255, 255, 0.08))
    return apply_theme(fig, "TurboQuant: Compression vs Quality")


# ── Chart 5: Source Distribution ──────────────────────────────────


def source_distribution(docs: list) -> go.Figure:
    """Bar chart of document counts by source."""
    source_counts: dict[str, int] = {}
    for d in docs:
        if isinstance(d, str):
            src = "unknown"
        elif hasattr(d, "source"):
            src = d.source
        elif isinstance(d, dict):
            src = d.get("source", "unknown")
        else:
            src = "unknown"
        source_counts[src] = source_counts.get(src, 0) + 1

    sources = sorted(source_counts.keys(), key=lambda s: source_counts[s], reverse=True)
    counts = [source_counts[s] for s in sources]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(sources))]

    fig = px.bar(
        x=counts,
        y=[s.replace("_", " ").title() for s in sources],
        orientation="h",
        color=counts,
        color_continuous_scale=[[0, BG_CARD], [1, ACCENT_GOLD]],
        labels={"x": "Documents", "y": "Source"},
    )
    fig.update_layout(
        xaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"gridcolor": RGBA(255, 255, 255, 0.08)},
        coloraxis_showscale=False,
    )
    return apply_theme(fig, "Corpus Composition")


# ── Chart 6: Emotion Timeline ─────────────────────────────────────


def emotion_timeline_chart(
    emotion_data: list[dict],
    year_metadata: dict[int, str] | None = None,
) -> go.Figure:
    """Emotion intensity over historical time."""
    # Simple version: just plot emotion scores by document index
    if not emotion_data:
        fig = go.Figure()
        return apply_theme(fig, "How Human Emotion Shifted Over 5,000 Years")

    top_emotions = sorted(
        {k for d in emotion_data for k in d.keys()
         if k not in ("source", "title", "text", "metadata") and isinstance(d.get(k, 0), (int, float))},
        key=lambda k: -np.mean([d.get(k, 0) for d in emotion_data if isinstance(d.get(k, 0), (int, float))])
    )[:5]

    fig = go.Figure()
    for i, emotion in enumerate(top_emotions):
        vals = [d.get(emotion, 0) for d in emotion_data if isinstance(d.get(emotion, 0), (int, float))]
        fig.add_trace(go.Scatter(
            x=list(range(len(vals))),
            y=vals,
            mode="lines",
            name=emotion,
            line={"color": PALETTE[i % len(PALETTE)], "width": 2},
        ))

    fig.update_layout(
        xaxis={"title": "Document Index", "gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"title": "Emotion Score", "gridcolor": RGBA(255, 255, 255, 0.08)},
        showlegend=True,
    )
    return apply_theme(fig, "How Human Emotion Shifted Over 5,000 Years")


# ── Chart 7: Topic Bar Chart ──────────────────────────────────────


def topic_barchart(topic_info: list[dict]) -> go.Figure:
    """Top words per topic as horizontal bars."""
    if not topic_info:
        fig = go.Figure()
        return apply_theme(fig, "Topics and Their Keywords")

    # Extract top topics (by size)
    topic_info_sorted = sorted(
        topic_info,
        key=lambda t: t.get("Count", t.get("count", 0)),
        reverse=True,
    )[:10]

    names = [str(t.get("Topic", t.get("topic", ""))) for t in topic_info_sorted]
    counts = [t.get("Count", t.get("count", 0)) for t in topic_info_sorted]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(names))]

    fig = go.Figure(
        go.Bar(
            y=names,
            x=counts,
            orientation="h",
            marker={"color": colors},
            hovertext=[str(t.get("Name", t.get("name", ""))) for t in topic_info_sorted],
        )
    )
    fig.update_layout(
        xaxis={"title": "Document Count", "gridcolor": RGBA(255, 255, 255, 0.08)},
        yaxis={"title": "Topic", "gridcolor": RGBA(255, 255, 255, 0.08)},
    )
    return apply_theme(fig, "Topics and Their Keywords")


# ── Chart 8: Word Cloud (Bubble) ──────────────────────────────────


def word_cloud_data(vocab_stats: list[dict]) -> go.Figure:
    """Bubble chart visualization of vocabulary frequency."""
    if not vocab_stats:
        fig = go.Figure()
        return apply_theme(fig, "Vocabulary Density")

    top_words = sorted(
        vocab_stats,
        key=lambda w: w.get("count", w.get("frequency", 0)),
        reverse=True,
    )[:50]

    fig = go.Figure()
    for i, word_data in enumerate(top_words):
        word = word_data.get("word", word_data.get("text", ""))
        count = word_data.get("count", word_data.get("frequency", 0))
        fig.add_trace(go.Scatter(
            x=[np.random.uniform(0, 10)],
            y=[np.random.uniform(0, 10)],
            mode="markers+text",
            text=[word[:10]],
            marker={
                "size": max(10, min(count * 2, 80)),
                "color": PALETTE[i % len(PALETTE)],
                "opacity": 0.7,
            },
            textfont={"size": max(10, min(count, 24))},
            showlegend=False,
        ))

    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor=BG_SECONDARY,
    )
    return apply_theme(fig, "Vocabulary Density")


# ── Chart 9: Radar Chart ──────────────────────────────────────────


def radar_chart(
    source_emotions: dict[str, dict],
) -> go.Figure:
    """Radar/spider chart comparing emotion profiles across sources.

    source_emotions: {"sacred": {"joy": 0.3, "fear": 0.5, ...}, "political": ..., "modern": ...}
    """
    if not source_emotions:
        fig = go.Figure()
        return apply_theme(fig, "Emotional DNA of Text Types")

    all_emotions = sorted({
        e for profile in source_emotions.values() for e in profile.keys()
    })

    fig = go.Figure()
    colors = [ACCENT_GOLD, ACCENT_CYAN, ACCENT_PINK, ACCENT_PURPLE]

    for i, (source_name, profile) in enumerate(source_emotions.items()):
        vals = [profile.get(em, 0) for em in all_emotions]
        vals.append(vals[0])  # Close the radar
        labels = list(all_emotions) + [all_emotions[0]]

        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=labels,
            fill="toself",
            name=source_name.replace("_", " ").title(),
            line={"color": colors[i % len(colors)], "width": 2},
            fillcolor=RGBA(255, 255, 255, 0.05),
        ))

    fig.update_layout(
        polar={
            "bgcolor": BG_SECONDARY,
            "radialaxis": {"visible": True, "gridcolor": RGBA(255, 255, 255, 0.1)},
            "angularaxis": {"gridcolor": RGBA(255, 255, 255, 0.1)},
        },
        showlegend=True,
    )
    return apply_theme(fig, "Emotional DNA of Text Types")


# ── Chart 10: Summary Stats ───────────────────────────────────────


def summary_stats(doc_stats: list[dict]) -> go.Figure:
    """Multi-panel dashboard: word count, emotion, topic coverage."""
    if not doc_stats:
        fig = go.Figure()
        return apply_theme(fig, "Corpus in Numbers")

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "Document Length Distribution",
            "Avg Emotion Score by Source",
            "Topic Coverage",
        ),
        vertical_spacing=0.12,
    )

    # Plot 1: Word count histogram
    word_counts = [d.get("word_count", len(d.get("text", "").split())) for d in doc_stats]
    fig.add_trace(
        go.Histogram(x=word_counts, nbinsx=30, marker={"color": ACCENT_GOLD}),
        row=1, col=1,
    )

    # Plot 2: Emotion bar by source
    source_emotion: dict[str, list[float]] = {}
    for d in doc_stats:
        src = d.get("source", "unknown")
        emotion_score = d.get("dominant_emotion_score", 0)
        if src not in source_emotion:
            source_emotion[src] = []
        source_emotion[src].append(emotion_score)
    sources = sorted(source_emotion.keys())
    avg_emotions = [np.mean(source_emotion[s]) for s in sources]
    fig.add_trace(
        go.Bar(x=sources, y=avg_emotions, marker={"color": ACCENT_CYAN}),
        row=2, col=1,
    )

    # Plot 3: Topic coverage
    topic_counts: dict[str, int] = {}
    for d in doc_stats:
        t = d.get("topic", "unknown")
        topic_counts[t] = topic_counts.get(t, 0) + 1
    topics = sorted(topic_counts.keys())
    fig.add_trace(
        go.Bar(x=topics, y=[topic_counts[t] for t in topics], marker={"color": ACCENT_PINK}),
        row=3, col=1,
    )

    fig.update_layout(
        height=900,
        showlegend=False,
        plot_bgcolor=BG_SECONDARY,
        paper_bgcolor=BG_PRIMARY,
    )
    fig.update_xaxes(gridcolor=RGBA(255, 255, 255, 0.08))
    fig.update_yaxes(gridcolor=RGBA(255, 255, 255, 0.08))
    return apply_theme(fig, "Corpus in Numbers")
