-- Marts: source-level summary statistics
-- Combines corpus and emotion data for dashboard metrics

WITH corpus_stats AS (
    SELECT
        source,
        COUNT(*) AS document_count,
        ROUND(AVG(word_count), 1) AS avg_words,
        SUM(word_count) AS total_words,
        ROUND(AVG(char_length), 1) AS avg_chars
    FROM {{ ref('staging_corpus') }}
    GROUP BY source
),
emotion_stats AS (
    SELECT
        source,
        dominant_emotion AS top_emotion,
        document_count AS emotion_docs,
        avg_word_count,
        avg_char_count
    FROM {{ ref('int_emotion_profiles') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY source ORDER BY document_count DESC) = 1
)

SELECT
    c.source,
    c.document_count,
    c.avg_words,
    c.total_words,
    e.top_emotion,
    e.emotion_docs
FROM corpus_stats c
LEFT JOIN emotion_stats e ON c.source = e.source
