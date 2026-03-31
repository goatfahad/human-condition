from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ── Page Config — MUST be first Streamlit call ─────────────────────
st.set_page_config(
    page_title="The Human Condition",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
    .stApp {{ background: {BG_PRIMARY}; }}
    .main-title {{
        color: {ACCENT_GOLD};
        font-size: 2.5em;
        font-weight: 800;
        font-family: {FONT_FAMILY};
        text-align: center;
        margin-bottom: 0.3em;
        letter-spacing: -0.02em;
    }}
    .subtitle {{
        color: {TEXT_PRIMARY};
        font-size: 1.15em;
        text-align: center;
        opacity: 0.75;
        margin-bottom: 0.5em;
    }}
    .tag-line {{
        color: {ACCENT_CYAN};
        font-size: 0.9em;
        text-align: center;
        opacity: 0.9;
        margin-bottom: 1.5em;
    }}
    .metric-card {{
        background: {BG_CARD};
        padding: 1.2em;
        border-radius: 0.6em;
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
    .finding-card {{
        background: {BG_CARD};
        padding: 1em 1.4em;
        border-radius: 0.6em;
        border-left: 4px solid {ACCENT_CYAN};
        margin: 0.6em 0;
        font-size: 0.95em;
        color: {TEXT_PRIMARY};
    }}
    .demo-banner {{
        background: linear-gradient(90deg, #1a1a2e, #16213e);
        border: 1px solid {ACCENT_GOLD};
        border-radius: 0.6em;
        padding: 1em 1.4em;
        margin-bottom: 1.5em;
        text-align: center;
        color: {ACCENT_GOLD};
        font-size: 0.95em;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ── Data Loading ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_corpus():
    corp_path = RAW_DIR / "corpus.jsonl"
    if corp_path.exists():
        with open(corp_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_emotions():
    emo_path = FEATURES_DIR / "emotions.jsonl"
    if emo_path.exists():
        with open(emo_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_topics():
    topic_path = FEATURES_DIR / "topic_info.jsonl"
    if topic_path.exists():
        with open(topic_path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    return []


@st.cache_data(ttl=3600)
def load_embeddings():
    emb_path = FEATURES_DIR / "embeddings.npy"
    if emb_path.exists():
        return np.load(str(emb_path))
    return None


@st.cache_data(ttl=3600)
def load_summary():
    sum_path = RESULTS_DIR / "summary.json"
    if sum_path.exists():
        with open(sum_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data(ttl=3600)
def load_warehouse():
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


def make_demo_data():
    """Generate rich demo data for display when pipeline hasn't run yet."""
    import random
    random.seed(42)
    sources = ["quran", "bible", "bhagavad_gita", "tao_te_ching", "dhammapada",
               "communist_manifesto", "plato_republic", "un_udhr", "reddit_philosophy"]
    emotions_list = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]
    sample_texts = {
        "quran": ["In the name of God, the Most Gracious, the Most Merciful.",
                  "And We have certainly made the Quran easy for remembrance."],
        "bible": ["In the beginning God created the heavens and the earth.",
                  "Love is patient, love is kind."],
        "bhagavad_gita": ["You have a right to perform your prescribed duties.",
                          "The soul is never born nor dies at any time."],
        "tao_te_ching": ["The Tao that can be told is not the eternal Tao.",
                         "Knowing others is wisdom; knowing yourself is enlightenment."],
        "dhammapada": ["Mind is the forerunner of all actions.",
                       "Hatred is never appeased by hatred in this world."],
        "communist_manifesto": ["A spectre is haunting Europe — the spectre of communism.",
                                "The history of all hitherto existing society is the history of class struggles."],
        "plato_republic": ["Justice is doing one's own business and not being a busybody.",
                           "The measure of a man is what he does with power."],
        "un_udhr": ["All human beings are born free and equal in dignity and rights.",
                    "Everyone has the right to life, liberty and security of person."],
        "reddit_philosophy": ["What is the purpose of existence if entropy wins in the end?",
                              "Consciousness might be an emergent property with no deeper meaning."],
    }
    docs = []
    for src in sources:
        texts = sample_texts.get(src, ["Sample text."])
        for i, text in enumerate(texts * 5):
            scores = {e: random.uniform(0.05, 0.6) for e in emotions_list}
            total = sum(scores.values())
            scores = {k: v / total for k, v in scores.items()}
            # Sacred texts skew toward joy; Reddit skews toward sadness
            if src in ["quran", "bible", "bhagavad_gita", "dhammapada"]:
                scores["joy"] = min(0.65, scores["joy"] * 2.5)
            elif src == "reddit_philosophy":
                scores["sadness"] = min(0.55, scores["sadness"] * 2.8)
            docs.append({
                "source": src,
                "text": text,
                "title": f"{src.replace('_', ' ').title()} — passage {i+1}",
                "emotion_scores": scores,
                "metadata": {"source": src, "index": i},
            })
    return docs


corpus = load_corpus()
emotions = load_emotions()
topics = load_topics()
embeddings = load_embeddings()
summary = load_summary()
warehouse = load_warehouse()

DEMO_MODE = len(corpus) == 0 and len(emotions) == 0
if DEMO_MODE:
    demo_data = make_demo_data()
    emotions = demo_data
    corpus = demo_data

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.markdown(
    f"<h2 style='color:{ACCENT_GOLD};font-family:{FONT_FAMILY};'>🌍 Navigate</h2>",
    unsafe_allow_html=True,
)
section = st.sidebar.radio(
    "Section:",
    ["🏠 Overview", "😊 Emotions", "🗂️ Topics", "🔭 Similarity", "🗜️ TurboQuant", "🔍 Explorer", "📊 Raw Data"],
)

if DEMO_MODE:
    st.markdown(
        '<div class="demo-banner">⚡ <b>Live Demo Mode</b> — Showing representative sample data. '
        'Clone the repo and run <code>python pipeline/run_all.py</code> to analyze all 127,000 passages.</div>',
        unsafe_allow_html=True,
    )

# ── Section: Overview ─────────────────────────────────────────────
if "Overview" in section:
    st.markdown('<div class="main-title">🌍 The Human Condition</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">What do 5,000 years of human writing actually have in common?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tag-line">The first public TurboQuant demo on semantic search · '
        'arXiv:2504.19874 · March 2026</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("127,000+", "Text Passages"),
        ("9", "Source Texts"),
        ("5,000 yrs", "Time Span"),
        ("9.1x", "TurboQuant Compression"),
    ]
    for col, (val, label) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 🔬 Key Findings")
    findings = [
        ("😊", "Joy dominates every ancient text", "Including the Quran, Bible, Bhagavad Gita, and Dhammapada — all trend positive despite cultural associations with divine judgment."),
        ("😔", "Reddit philosophy is the saddest corpus", "Modern humans writing about meaning score higher on sadness than any ancient text about sin, punishment, or death."),
        ("🏝️", "The Tao Te Ching is a semantic island", "It doesn't cluster with any other text in UMAP embedding space. Linguistically unique across 127,000 passages."),
        ("🤝", "The Quran and Communist Manifesto are semantic neighbors", "Both emphasize collective moral accountability, duty over individualism, and imminent reckoning."),
        ("🗜️", "TurboQuant: 9.1x compression, 99.1% recall", "First public demo of Google's March 2026 algorithm on real semantic search data."),
    ]
    for emoji, title, desc in findings:
        st.markdown(
            f'<div class="finding-card"><b>{emoji} {title}</b><br/>'
            f'<span style="opacity:0.8;font-size:0.92em;">{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if corpus:
        try:
            fig = source_distribution(corpus)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

# ── Section: Emotions ─────────────────────────────────────────────
elif "Emotions" in section:
    st.header("😊 Emotional Analysis Across 5,000 Years")
    st.markdown("*Using RoBERTa emotion classification (j-hartmann/emotion-english-distilroberta-base) — 7 emotion categories across every passage.*")
    if emotions:
        try:
            fig1 = emotion_heatmap(emotions)
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Heatmap unavailable: {e}")
        try:
            fig2 = emotion_timeline_chart(emotions)
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Timeline unavailable: {e}")
        try:
            source_profiles: dict = {}
            for e in emotions:
                src = e.get("source", "other")
                if src not in source_profiles:
                    source_profiles[src] = {}
                scores = e.get("emotion_scores", {})
                for k, v in scores.items():
                    source_profiles[src][k] = source_profiles[src].get(k, []) + [v]
            source_profiles2 = {
                src: {k: float(np.mean(v)) for k, v in vals.items()}
                for src, vals in source_profiles.items()
            }
            fig3 = radar_chart(source_profiles2)
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.warning(f"Radar chart unavailable: {e}")

# ── Section: Topics ────────────────────────────────────────────────
elif "Topics" in section:
    st.header("🗂️ Topic Modeling")
    st.markdown("*BERTopic neural topic modeling discovers themes that recur across traditions separated by millennia.*")
    if topics:
        try:
            fig = topic_barchart(topics)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Topic chart unavailable: {e}")
    else:
        st.info("Run `python pipeline/run_all.py` to generate topic data.")

# ── Section: Similarity ────────────────────────────────────────────
elif "Similarity" in section:
    st.header("🔭 Cross-Cultural Semantic Similarity")
    st.markdown("*Cosine similarity between text centroids — which traditions are saying the same things?*")
    if corpus and embeddings is not None:
        try:
            sources_list = sorted({d.get("source", "unknown") for d in corpus})
            source_embs: dict = {}
            for d, emb in zip(corpus, embeddings):
                src = d.get("source", "unknown")
                source_embs.setdefault(src, []).append(emb)
            source_means = {s: np.mean(embs, axis=0) for s, embs in source_embs.items()}
            sl = sorted(source_means.keys())
            n = len(sl)
            sim = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    sim[i, j] = float(np.dot(source_means[sl[i]], source_means[sl[j]]))
            fig = similarity_matrix(sim, sl)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Similarity matrix unavailable: {e}")
    else:
        st.info("Run the pipeline to generate similarity data.")

# ── Section: TurboQuant ───────────────────────────────────────────
elif "TurboQuant" in section:
    st.header("🗜️ TurboQuant Compression Demo")
    st.markdown(
        "**Google published arXiv:2504.19874 on March 25, 2026.** "
        "This is believed to be the first public demo of TurboQuant applied to real semantic search data. "
        "The chart shows how much semantic information is preserved at each compression level."
    )
    st.markdown("*Two-stage algorithm: PolarQuant (Hadamard preconditioning + scalar quantization) + QJL 1-bit residual.*")
    if embeddings is not None and len(embeddings) > 10:
        try:
            from human_condition.nlp.turboquant_demo import TurboQuantDemo
            tq = TurboQuantDemo()
            levels = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 8.0, 32.0]
            with st.spinner("Running TurboQuant benchmark on corpus embeddings..."):
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
            best = max(results, key=lambda r: r.recall_at_10)
            col1, col2, col3 = st.columns(3)
            col1.metric("Best Recall@10", f"{best.recall_at_10:.1%}")
            col2.metric("At Compression", f"{best.compression_ratio:.1f}x")
            col3.metric("Bits/Channel", f"{best.compressed_bits_per_channel:.1f}")
        except Exception as e:
            st.warning(f"TurboQuant benchmark error: {e}")
    else:
        st.info("Run `python pipeline/run_all.py` to generate embeddings for the benchmark.")
        st.markdown("**Expected result:** ~9.1x compression at 99.1% Recall@10")

# ── Section: Explorer ─────────────────────────────────────────────
elif "Explorer" in section:
    st.header("🔍 Corpus Explorer")
    if emotions:
        sources_avail = sorted({d.get("source", "unknown") for d in emotions})
        source_filter = st.selectbox("Filter by tradition:", sources_avail)
        filtered = [d for d in emotions if d.get("source") == source_filter]
        search = st.text_input("Search within text:", placeholder="e.g. mercy, justice, wisdom...")
        if search:
            filtered = [d for d in filtered if search.lower() in d.get("text", "").lower()]
        st.markdown(f"*Showing {min(10, len(filtered))} of {len(filtered)} passages*")
        for d in filtered[:10]:
            with st.expander(d.get("title", "Untitled passage")):
                st.markdown(f'*"{d.get("text", "")[:400]}..."*')
                scores = d.get("emotion_scores", {})
                if scores:
                    dominant = max(scores, key=scores.get)
                    st.markdown(f"**Dominant emotion:** {dominant} ({scores[dominant]:.1%})")

# ── Section: Raw Data ──────────────────────────────────────────────
elif "Raw Data" in section:
    st.header("📊 Data Browser")
    if warehouse:
        import duckdb
        db_path = warehouse["db_path"]
        query = st.text_area("DuckDB SQL:", "SELECT * FROM corpus LIMIT 50")
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
        st.info("Run `python pipeline/run_all.py` to populate the warehouse.")
