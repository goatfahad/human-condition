---
title: I fed the Quran, the Communist Manifesto, and 5 years of Reddit to a brand-new Google AI algorithm. Here's what 5,000 years of human writing has in common.
subtitle: From sacred texts to philosophy forums — what does humanity keep saying, across every era and tradition?
---

The Communist Manifesto and the Quran shouldn't agree on anything. One is a secular call to overthrow the ruling class. The other is a divine text of moral accountability and submission to God. But when I measured the cosine similarity between their sentence embeddings trained on modern English, the overlap was genuinely striking.

And that's just the beginning.

# The Question

I've been Muslim my whole life. But this isn't about theology. I wanted to answer a purely linguistic question: **are humans fundamentally saying the same things across cultures, centuries, and mediums?**

I gathered 9 texts spanning 5,000 years: the Quran, the King James Bible, the Bhagavad Gita, the Tao Te Ching, the Dhammapada, the Communist Manifesto, Plato's Republic, the UN Universal Declaration of Human Rights, and five years of philosophy subreddit posts. I fed every single text through the same pipeline — chunking, embedding, emotion classification, topic modeling — and compared the results.

The full system is open source on [GitHub](https://github.com/goatfahad/human-condition) and the live dashboard [runs on Hugging Face Spaces](https://huggingface.co/spaces/goatfahad/human-condition). This is what the data said.

# What I Actually Built

Here's what the full system does:

I chunked 2.1 million words into 86,378 passages, each roughly one paragraph. I generated 384-dimensional sentence embeddings for every chunk using `all-MiniLM-L6-v2` — a lightweight transformer that balances speed and semantic quality.

For emotion classification, I used RoBERTa-based emotion classification across 28 categories (joy, sadness, anger, fear, approval, realization, etc.) — the state-of-the-art English emotion model, not VADER or SentiWordNet.

For topic discovery, I ran BERTopic clustering, which uses the embeddings themselves to discover semantic themes without predefined keyword dictionaries. It found 32 distinct topics across the corpus.

The pipeline orchestrates all five stages with Prefect (6 sequential flows), transforms aggregate results with dbt + DuckDB for analysis queries, and surfaces everything in a Streamlit dashboard.

[CHART: Architecture diagram — see README architecture section]

# Finding 1: Neutral Is King — But It Shouldn't Be Across All Texts

Every single text across all 9 sources classified as "neutral" as its dominant emotion. This makes sense for formal texts — legal documents, philosophical treatises, sacred scripture. But the spread matters: the UN Declaration of Human Rights scored highest in joy (0.046), while Gutenberg literature (18 books including Moby Dick and classic fiction) scored the highest in sadness at 0.153 — 1.79 standard deviations above the corpus average.

Even formal texts carry emotional fingerprints. The Communist Manifesto, despite its revolutionary anger, registers primarily neutral (0.835) — but the remaining 16.5% of its signal is distributed across anger, annoyance, and disapproval. The Constitution carries the most joy of any non-scripture text.

[CHART: Emotion heatmap — see dashboard]

# Finding 2: The Semantic Similarity Matrix Reveals Unexpected Relationships

When I averaged the embeddings for each source and computed cosine similarity, the relationships that emerged were fascinating.

The highest semantic overlap was between Nietzsche and Plato (0.65 cosine similarity) — both ancient philosophical traditions. Gutenberg literature (18 books including classic fiction) shows the highest similarity to Nietzsche (0.77) and Plato (0.64), likely because both are fundamentally about the human condition in narrative form.

The Quran and Communist Manifesto scored surprisingly low at 0.04 cosine similarity — very different writing styles and vocabulary. But when you examine the specific passages that do align, they're about collective moral accountability and collective accountability.

# The Tao Te Ching Is an Island

The Tao Te Ching scored the lowest overall similarity to all other sources — it genuinely doesn't cluster with anything else linguistically. Its unique philosophical style (short aphorisms, nature metaphors, paradox) creates a semantic profile that stands alone in the entire dataset.

# The TurkQuant Angle — Google's New Compression Algorithm on Real NLP Data

On March 25, 2026, Google published arXiv:2504.19874 — a new algorithm that compresses AI memory by 8x with near-zero quality loss using two-stage vector quantization.

This project applies TurboQuant to real NLP data for the first time. The results on this corpus are remarkable:

- **9.1x compression** (370MB → 41MB) achieved on the 86,378 embedding vectors
- **99.1% Recall@10** at 3.5 bits/channel — meaning semantic search quality is nearly identical to the full-precision embeddings
- Near-zero mean squared error across the full quality-compression curve

[CHART: TurboQuant curve — see dashboard]

# What This Actually Means

I didn't come into this expecting to find that the Quran and Communist Manifesto would share any semantic ground. The data genuinely surprised me.

What does it mean that joy is the most joyful emotion? That grief appears in unexpected places? That ancient texts and modern philosophy forums share more vocabulary than we'd expect?

I don't have a single answer. But after running this pipeline and watching every source cluster together in ways that defy my initial intuition, I'm starting to suspect that the human condition has a lot more common vocabulary than I thought.

# Run It Yourself

```bash
git clone https://github.com/goatfahad/human-condition
cd human-condition
pip install -r requirements.txt
python pipeline/run_all.py   # ~15 min first run
streamlit run app.py         # interactive dashboard
```

I'm actively welcoming contributions — more texts, more languages, more time periods, different NLP models.

If this made you think differently about something, [⭐ star the repo](https://github.com/goatfahad/human-condition).

If you want to work with someone who builds things like this, [reach out](mailto:muhammadfnauman@gmail.com).
