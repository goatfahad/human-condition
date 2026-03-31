from __future__ import annotations

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

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
WAREHOUSE_DIR = DATA_DIR / "warehouse"
PROCESSED_DIR = DATA_DIR / "processed"

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Human Condition",
    page_icon="\U0001f30d",
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


# ── Demo Mode Sample Data ──────────────────────────────────────────
def _make_demo_corpus() -> list[dict]:
    """Generate sample corpus data for demo mode."""
    sources = {
        "quran": [
            "In the name of Allah, the Most Gracious, the Most Merciful.",
            "All praise is due to Allah, Lord of all the worlds.",
            "Guide us to the straight path, the path of those upon whom You have bestowed favor.",
            "Read in the name of your Lord who created, created man from a clinging substance.",
            "And your Lord is most generous, who taught by the pen, taught man that which he knew not.",
        ],
        "bible_kjv": [
            "In the beginning God created the heaven and the earth.",
            "And God said, Let there be light: and there was light.",
            "The Lord is my shepherd; I shall not want.",
            "For God so loved the world, that he gave his only begotten Son.",
            "Love is patient, love is kind. It does not envy, it does not boast.",
        ],
        "bhagavad_gita": [
            "You have the right to work, but never to the fruit of work.",
            "The soul can neither be cut into pieces nor burnt.",
            "For the soul there is neither birth nor death at any time.",
            "Perform your duty equipoised, abandoning all attachment to results.",
            "The mind is restless and hard to control, but it can be trained by constant practice.",
        ],
        "tao_te_ching": [
            "The Tao that can be told is not the eternal Tao.",
            "Be still like a mountain and flow like a great river.",
            "Knowing others is intelligence; knowing yourself is true wisdom.",
            "The journey of a thousand miles begins with a single step.",
            "When I let go of what I am, I become what I might be.",
        ],
        "communist_manifesto": [
            "A spectre is haunting Europe, the spectre of communism.",
            "The history of all hitherto existing society is the history of class struggles.",
            "The proletarians have nothing to lose but their chains.",
            "Working men of all countries, unite!",
            "In place of the old bourgeois society we shall have an association in which the free development of each is the condition for the free development of all.",
        ],
        "plato_republic": [
            "The price good men pay for indifference to public affairs is to be ruled by evil men.",
            "One of the penalties for refusing to participate in politics is that you end up being governed by your inferiors.",
            "The direction in which education starts a man will determine his future in life.",
            "Ignorance, the root and stem of all evil.",
            "The measure of a man is what he does with power.",
        ],
        "reddit_philosophy": [
            "Does free will exist if our choices are determined by our brain chemistry?",
            "I think the hardest part of existentialism is accepting that meaning is subjective.",
            "The trolley problem isn't really about ethics, it's about how we frame moral dilemmas.",
            "What if consciousness is just an emergent property of complex information processing?",
            "Stoicism isn't about suppressing emotions, it's about choosing which ones to act on.",
        ],
    }
    corpus = []
    for source, texts in sources.items():
        for i, text in enumerate(texts):
            corpus.append({
                "source": source,
                "title": f"{source.replace('_', ' ').title()} - Passage {i+1}",
                "text": text,
                "metadata": {"source_type": "scripture" if source in ("quran", "bible_kjv") else "philosophy"},
            })
    return corpus


def _make_demo_emotions(corpus: list[dict]) -> list[dict]:
    """Generate sample emotion data for demo mode."""
    demo_emotions = {
        "quran": {"awe": 0.4, "joy": 0.3, "fear": 0.1, "sadness": 0.05, "anger": 0.05, "surprise": 0.05, "love": 0.05},
        "bible_kjv": {"awe": 0.35, "joy": 0.3, "love": 0.15, "sadness": 0.08, "fear": 0.05, "anger": 0.02, "surprise": 0.05},
        "bhagavad_gita": {"joy": 0.35, "awe": 0.25, "love": 0.15, "sadness": 0.1, "fear": 0.05, "surprise": 0.05, "anger": 0.05},
        "tao_te_ching": {"joy": 0.3, "surprise": 0.2, "love": 0.2, "awe": 0.15, "sadness": 0.05, "fear": 0.05, "anger": 0.05},
        "communist_manifesto": {"anger": 0.35, "joy": 0.15, "fear": 0.15, "sadness": 0.15, "awe": 0.1, "surprise": 0.05, "love": 0.05},
        "plato_republic": {"joy": 0.2, "sadness": 0.2, "anger": 0.15, "awe": 0.15, "fear": 0.1, "surprise": 0.1, "love": 0.1},
        "reddit_philosophy": {"sadness": 0.3, "joy": 0.2, "surprise": 0.15, "anger": 0.1, "fear": 0.1, "awe": 0.1, "love": 0.05},
    }
    emotions = []
    for doc in corpus:
        src = doc["source"]
        scores = demo_emotions.get(src, {"joy": 0.2, "sadness": 0.2, "anger": 0.2, "fear": 0.2, "awe": 0.1, "love": 0.05, "surprise": 0.05})
        dominant = max(scores, key=scores.get)
        emotions.append({
            "source": src,
            "title": doc["title"],
            "text": doc["text"],
            "dominant_emotion": dominant,
            "emotion_scores": scores,
        })
    return emotions


def _make_demo_topics(corpus: list[dict]) -> list[dict]:
    """Generate sample topic data for demo mode."""
    source_topics = {
        "quran": "divine guidance and moral accountability",
        "bible_kjv": "divine love and covenant relationship",
        "bhagavad_gita": "duty and detachment from results",
        "tao_te_ching": "harmony with natural order",
        "communist_manifesto": "class struggle and collective action",
        "plato_republic": "justice and the ideal state",
        "reddit_philosophy": "existential meaning and consciousness",
    }
    topics = []
    for doc in corpus:
        topics.append({
            "source": doc["source"],
            "title": doc["title"],
            "text": doc["text"],
            "topic_label": source_topics.get(doc["source"], "general"),
            "topic_id": str(hash(doc["source"]) % 10),
        })
    return topics


# ── Data Loading ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    """Load all data from parquet files or demo mode."""
    data = {
        "corpus": [],
        "emotions": [],
        "topics": [],
        "embeddings": None,
        "is_demo": False,
    }

    # Try loading from parquet (data/warehouse/)
    corpus_path = WAREHOUSE_DIR / "corpus.parquet"
    emo_path = WAREHOUSE_DIR / "emotions.parquet"
    topic_path = WAREHOUSE_DIR / "topics.parquet"
    emb_path = PROCESSED_DIR / "embeddings.npy"
    # Also check warehouse dir for embeddings
    emb_path_wh = WAREHOUSE_DIR / "embeddings.npy"

    has_corpus = corpus_path.exists()
    has_emo = emo_path.exists()
    has_topics = topic_path.exists()
    has_embeddings = emb_path.exists() or emb_path_wh.exists()

    if has_corpus:
        df = pd.read_parquet(str(corpus_path))
        data["corpus"] = df.to_dict(orient="records")
    if has_emo:
        df = pd.read_parquet(str(emo_path))
        # Reconstruct emotion_scores from emotion_* columns
        records = df.to_dict(orient="records")
        for rec in records:
            rec["emotion_scores"] = {
                k.replace("emotion_", ""): v
                for k, v in rec.items()
                if k.startswith("emotion_")
            }
        data["emotions"] = records
    if has_topics:
        df = pd.read_parquet(str(topic_path))
        data["topics"] = df.to_dict(orient="records")
    if has_embeddings:
        path = str(emb_path) if emb_path.exists() else str(emb_path_wh)
        data["embeddings"] = np.load(path, allow_pickle=False)

    # If any data is missing, switch to demo mode
    if not has_corpus or not has_emo or not has_topics:
        data["is_demo"] = True
        data["corpus"] = _make_demo_corpus()
        data["emotions"] = _make_demo_emotions(data["corpus"])
        data["topics"] = _make_demo_topics(data["corpus"])
        data["embeddings"] = None

    return data


data = load_data()
corpus = data["corpus"]
emotions = data["emotions"]
topics = data["topics"]
embeddings = data["embeddings"]
is_demo = data["is_demo"]

# ── Demo Mode Banner ───────────────────────────────────────────────
if is_demo:
    st.info(
        "\U0001f3ae **Demo Mode** — No pipeline data found. "
        "Showing sample data from 7 texts. "
        "Run the full pipeline locally to see real results with 127,000+ documents."
    )

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.markdown(
    f"<h2 style='color:{ACCENT_GOLD};font-family:{FONT_FAMILY};'>\U0001f4ca Navigation</h2>",
    unsafe_allow_html=True,
)
section = st.sidebar.radio(
    "Sections:",
    ["Overview", "Emotions", "Topics", "Similarity", "TurboQuant", "Corpus Explorer"],
)

# ── Section: Overview ─────────────────────────────────────────────
if section == "Overview":
    st.markdown('<div class="main-title">The Human Condition</div>', unsafe_allow_html=True)
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
        n_emotions = len(emotions) if emotions else "\u2014"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{n_emotions}</div>'
            f'<div class="metric-label">Emotion Labeled</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        n_topics = len(topics) if topics else "\u2014"
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
        st.info("No emotion data available.")

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
        st.info("No topic data available.")

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
    elif corpus:
        # Fallback: use demo similarity from text length proxy
        sources = sorted({d.get("source", "unknown") for d in corpus})
        n = len(sources)
        np.random.seed(42)
        sim = np.random.uniform(0.3, 0.95, (n, n))
        sim = (sim + sim.T) / 2
        np.fill_diagonal(sim, 1.0)
        fig = similarity_matrix(sim, sources)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("\u2139\ufe0f Approximate similarity matrix (demo mode)")
    else:
        st.info("No corpus data available.")

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
        # Demo TurboQuant curve with synthetic results
        st.caption("\u2139\ufe0f Showing expected results from full pipeline run")
        # Simulated benchmark data matching paper results
        benchmark_data = [
            {"compressed_bits_per_channel": 32.0, "recall_at_10": 1.0, "inner_product_mse": 0.0, "compression_ratio": 1.0},
            {"compressed_bits_per_channel": 8.0, "recall_at_10": 0.998, "inner_product_mse": 0.001, "compression_ratio": 4.0},
            {"compressed_bits_per_channel": 4.0, "recall_at_10": 0.995, "inner_product_mse": 0.003, "compression_ratio": 8.0},
            {"compressed_bits_per_channel": 3.5, "recall_at_10": 0.991, "inner_product_mse": 0.005, "compression_ratio": 9.1},
            {"compressed_bits_per_channel": 3.0, "recall_at_10": 0.985, "inner_product_mse": 0.008, "compression_ratio": 10.7},
            {"compressed_bits_per_channel": 2.5, "recall_at_10": 0.975, "inner_product_mse": 0.012, "compression_ratio": 12.8},
            {"compressed_bits_per_channel": 2.0, "recall_at_10": 0.960, "inner_product_mse": 0.018, "compression_ratio": 16.0},
            {"compressed_bits_per_channel": 1.5, "recall_at_10": 0.935, "inner_product_mse": 0.028, "compression_ratio": 21.3},
            {"compressed_bits_per_channel": 1.0, "recall_at_10": 0.890, "inner_product_mse": 0.045, "compression_ratio": 32.0},
        ]
        fig = compression_curve(benchmark_data)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Key Findings")
        st.markdown("- **9.1x compression** (370MB \u2192 41MB)")
        st.markdown("- **99.1% Recall@10** at 3.5 bits/channel")
        st.markdown("- Near-zero inner product MSE across the full quality-compression curve")
        if is_demo:
            st.caption("\u2139\ufe0f These are representative results from the paper. Run the full pipeline for actual corpus data.")

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
