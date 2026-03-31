"""Streamlit dashboard for The Human Condition v2.0."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from human_condition.viz.charts import (
    apply_theme,
    compression_curve,
    emotion_heatmap,
    radar_chart,
    similarity_matrix,
    source_distribution,
    summary_stats,
    topic_barchart,
    topic_scatter,
    word_cloud_data,
    emotion_timeline_chart,
)
from human_condition.viz.theme import (
    ACCENT_GOLD,
    ACCENT_CYAN,
    ACCENT_PINK,
    ACCENT_PURPLE,
    BG_CARD,
    BG_PRIMARY,
    FONT_FAMILY,
    PALETTE,
    PLOTLY_TEMPLATE,
    TEXT_PRIMARY,
)

# ── Paths ──────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = DATA_DIR / "results"
FEATURES_DIR = DATA_DIR / "features"
RAW_DIR = DATA_DIR / "raw"

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Human Condition v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
    .stApp {{ background: {BG_PRIMARY}; }}
    .main-title {{
        color: {ACCENT_GOLD};
        font-size: 2.2em;
        font-family: {FONT_FAMILY};
        text-align: center;
        margin-bottom: 0.5em;
    }}
    .subtitle {{
        color: {TEXT_PRIMARY};
        font-size: 1.1em;
        text-align: center;
        opacity: 0.8;
    }}
    .metric-card {{
        background: {BG_CARD};
        padding: 1.2em;
        border-radius: 0.5em;
        border-left: 4px solid {ACCENT_GOLD};
        margin: 0.5em 0;
    }}
    .metric-value {{
        font-size: 1.8em;
        font-weight: bold;
        color: {ACCENT_GOLD};
    }}
    .metric-label {{
        font-size: 0.85em;
        color: #A0A0A0;
        margin-top: 0.3em;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ── Data Loading ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_corpus():
    """Load corpus from raw JSONL."""
    corp_path = RAW_DIR / "corpus.jsonl"
    if corp_path.exists():
        with open(corp_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_emotions():
    """Load emotion-classified documents."""
    emo_path = FEATURES_DIR / "emotions.jsonl"
    if emo_path.exists():
        with open(emo_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_topics():
    """Load topic modeling results."""
    topic_path = FEATURES_DIR / "topic_info.jsonl"
    if topic_path.exists():
        with open(topic_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_embeddings():
    """Load embeddings array."""
    emb_path = FEATURES_DIR / "embeddings.npy"
    if emb_path.exists():
        return np.load(str(emb_path))
    return None


@st.cache_data(ttl=3600)
def load_summary():
    """Load summary stats."""
    sum_path = RESULTS_DIR / "summary.json"
    if sum_path.exists():
        with open(sum_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data(ttl=3600)
def load_warehouse():
    """DuckDB connection info / query helper."""
    db_path = DATA_DIR / "warehouse.duckdb"
    if db_path.exists():
        try:
            import duckdb

            con = duckdb.connect(str(db_path), read_only=True)
            tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
            return {"tables": tables, "db_path": str(db_path)}
        except Exception:
            return None
    return None


corpus = load_corpus()
emotions = load_emotions()
topics = load_topics()
embeddings = load_embeddings()
summary = load_summary()
warehouse = load_warehouse()

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.markdown(
    f"<h2 style='color:{ACCENT_GOLD};font-family:{FONT_FAMILY};'>📊 Navigation</h2>",
    unsafe_allow_html=True,
)
section = st.sidebar.radio(
    "Sections:",
    ["Overview", "Emotions", "Topics", "Similarity", "TurboQuant", "Corpus Explorer", "Raw Data"],
)

# ── Section: Overview ─────────────────────────────────────────────
if section == "Overview":
    st.markdown('<div class="main-title">The Human Condition v2.0</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">5,000 years of human writing analyzed through NLP and AI.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</br>")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{len(corpus)}</div>'
            f'<div class="metric-label">Documents</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        total_words = sum(len(d.get("text", "").split()) for d in corpus)
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{total_words:,}</div>'
            f'<div class="metric-label">Total Words</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        n_emotions = len(emotions) if emotions else "—"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{n_emotions}</div>'
            f'<div class="metric-label">Emotion Labeled</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        n_topics = len(topics) if topics else "—"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{n_topics}</div>'
            f'<div class="metric-label">Topics Found</div></div>',
            unsafe_allow_html=True,
        )

    if corpus:
        fig = source_distribution(corpus)
        st.plotly_chart(fig, use_container_width=True)

    if emotions:
        stats = []
        for e in emotions:
            stats.append(
                {
                    "source": e.get("source", "unknown"),
                    "word_count": len(e.get("text", "").split()),
                    "dominant_emotion_score": next(
                        iter(e.get("emotion_scores", {}).values()), 0
                    ),
                    "topic": "unknown",
                    "text": e.get("text", ""),
                }
            )
        fig = summary_stats(stats)
        st.plotly_chart(fig, use_container_width=True)

    if not corpus:
        st.info("No data loaded yet. Run the Airflow pipeline to populate the warehouse.")

# ── Section: Emotions ─────────────────────────────────────────────
elif section == "Emotions":
    st.header("Emotional Analysis")
    if emotions:
        fig1 = emotion_heatmap(emotions)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = emotion_timeline_chart(emotions)
        st.plotly_chart(fig2, use_container_width=True)

        source_profiles = {}
        for e in emotions:
            src = e.get("source", "other")
            if src not in source_profiles:
                source_profiles[src] = {}
            scores = e.get("emotion_scores", {})
            for k, v in scores.items():
                source_profiles[src][k] = source_profiles[src].get(k, []) + [v]
        source_profiles2 = {}
        for src, vals in source_profiles.items():
            source_profiles2[src] = {k: float(np.mean(v)) for k, v in vals.items()}
        fig3 = radar_chart(source_profiles2)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No emotion data available. Run the analyze DAG first.")

# ── Section: Topics ────────────────────────────────────────────────
elif section == "Topics":
    st.header("Topic Modeling")
    if topics:
        fig = topic_barchart(topics)
        st.plotly_chart(fig, use_container_width=True)

        if embeddings is not None and len(embeddings) > 2:
            from sklearn.decomposition import PCA
            emb_2d = PCA(n_components=2).fit_transform(embeddings)
            topic_labels = list(range(len(topics)))
            fig2 = topic_scatter(emb_2d, topic_labels)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Embeddings not available for scatter plot.")
    else:
        st.info("No topic data available. Run the topics DAG first.")

# ── Section: Similarity ────────────────────────────────────────────
elif section == "Similarity":
    st.header("Cross-Century Similarity")
    if corpus and embeddings is not None:
        sources = sorted({d.get("source", "unknown") for d in corpus})
        source_embs = {}
        for d, emb in zip(corpus, embeddings):
            src = d.get("source", "unknown")
            source_embs.setdefault(src, []).append(emb)
        source_means = {s: np.mean(embs, axis=0) for s, embs in source_embs.items()}
        source_list = sorted(source_means.keys())
        n = len(source_list)
        sim = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                sim[i, j] = float(np.dot(source_means[source_list[i]], source_means[source_list[j]]))
        fig = similarity_matrix(sim, source_list)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run the pipeline first to generate similarity data.")

# ── Section: TurboQuant ───────────────────────────────────────────
elif section == "TurboQuant":
    st.header("TurboQuant Compression Demo")
    st.write(
        "This demonstrates KV cache compression on our corpus embeddings. "
        "It shows how much information is retained at various compression levels."
    )
    if embeddings is not None and len(embeddings) > 10:
        from human_condition.nlp.turboquant_demo import TurboQuantDemo

        tq = TurboQuantDemo()
        levels = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 8.0, 32.0]
        with st.spinner("Running TurboQuant benchmark..."):
            results = tq.benchmark_compression_levels(embeddings[:500], levels)

        benchmark_data = [
            {
                "compressed_bits_per_channel": r.compressed_bits_per_channel,
                "recall_at_10": r.recall_at_10,
                "inner_product_mse": r.inner_product_mse,
                "compression_ratio": r.compression_ratio,
            }
            for r in results
        ]
        fig = compression_curve(benchmark_data)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Key Findings")
        best = max(results, key=lambda r: r.recall_at_10)
        st.markdown(
            f"- **Best recall**: {best.recall_at_10:.1%} at {best.compression_ratio:.1f}x compression"
        )
    else:
        st.info("Run the embed DAG first to generate embeddings.")

# ── Section: Corpus Explorer ───────────────────────────────────────
elif section == "Corpus Explorer":
    st.header("Explore the Corpus")
    if emotions:
        sources = sorted({d.get("source", "unknown") for d in emotions})
        source_filter = st.selectbox("Filter by source:", sources)
        filtered = [d for d in emotions if d.get("source") == source_filter]
        search = st.text_input("Search text:")
        if search:
            filtered = [d for d in filtered if search.lower() in d.get("text", "").lower()]
        for d in filtered[:10]:
            with st.expander(d.get("title", "Untitled")):
                st.text(d.get("text", "")[:500])
                st.markdown(f"Source: `{d.get('source')}`")
                meta = d.get("metadata", {})
                if isinstance(meta, dict):
                    st.json(meta)
        if len(filtered) > 10:
            st.info(f"Showing 10 of {len(filtered)} results.")
    else:
        st.info("No corpus data available.")

# ── Section: Raw Data ──────────────────────────────────────────────
elif section == "Raw Data":
    st.header("Raw Data Browser")
    if warehouse:
        import duckdb

        db_path = warehouse["db_path"]
        query = st.text_area(
            "Enter DuckDB SQL query:",
            "SELECT * FROM corpus LIMIT 100",
        )
        if st.button("Run Query"):
            con = duckdb.connect(str(db_path), read_only=True)
            try:
                df = con.execute(query).df()
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Query error: {e}")
            finally:
                con.close()
    else:
        st.info("DuckDB warehouse not found. Run the export DAG first.")

        st.subheader("Available Raw Files")
        for path in [RAW_DIR / "corpus.jsonl", FEATURES_DIR / "emotions.jsonl", FEATURES_DIR / "topic_info.jsonl"]:
            if path.exists():
                n_lines = sum(1 for _ in open(path, encoding="utf-8"))
                st.markdown(f"- **{path.name}**: {n_lines:,} records ({path.parent})")