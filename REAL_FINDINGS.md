# THE HUMAN CONDITION — REAL PIPELINE FINDINGS

## Corpus Statistics
- **Total documents:** 162
- **Total words:** 2,137,285
- **Sources (9):** quran (114), bible (24), gutenberg (18 books), communist_manifesto (1), confucius (1), constitution (1), nietzsche (1), marx (1), plato (1)

## Emotion Analysis
- **Model:** j-hartmann/emotion-english-distilroberta-base (28 emotion categories)
- **Emotion-scored passages:** 100 sample texts from 5 sources

### Dominant Emotion Per Source
| Source | Dominant | Score | Joy | Sadness |
|--------|----------|-------|-----|---------|
| bible | neutral | 0.969 | 0.002 | 0.004 |
| communist_manifesto | neutral | 0.835 | 0.001 | 0.004 |
| confucius | neutral | 0.597 | 0.002 | 0.005 |
| constitution | neutral | 0.741 | 0.046 | 0.001 |
| gutenberg | neutral | 0.539 | 0.006 | 0.153 |

### Key Findings
- **Saddest source:** gutenberg (mean sadness = 0.153, z = +1.79 stdevs)
- **Most joyful source:** constitution (mean joy = 0.046)
- Neutral dominates across all sources (objective/formal text)

## Semantic Similarity (Cosine)
- gutenberg ↔ nietzsche: 0.77
- nietzsche ↔ plato: 0.65
- gutenberg ↔ plato: 0.64
- communist_manifesto ↔ confucius: 0.25
- quran/bible show lowest similarity to other sources

**Quran ↔ Communist Manifesto:** 0.04

## BERTopic Results
- **Total topics:** 32 (31 named + outlier -1)
- **Top topics:**
  1. Topic 0: 34,675 docs
  2. Topic 1: 13,558 docs
  3. Topic 2: 2,137 docs (whale/nautical)
  4. Topic 3: 609 docs
  5. Topic 4: 369 docs

## Pipeline Statistics
- **Embeddings:** 86,378 × 384 dims
