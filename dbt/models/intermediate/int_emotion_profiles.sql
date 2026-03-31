"""Intermediate: emotion profiles aggregated by source."""

WITH emotion_base AS (
    SELECT
        source,
        dominant_emotion,
        word_count,
        char_length
    FROM {{ ref('stg_emotions') }}
)

SELECT
    source,
    dominant_emotion,
    COUNT(*) AS document_count,
    ROUND(AVG(word_count), 1) AS avg_words,
    ROUND(AVG(char_length), 1) AS avg_chars
FROM emotion_base
GROUP BY source, dominant_emotion
