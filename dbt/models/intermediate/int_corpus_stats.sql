-- Intermediate: emotion profiles aggregated by source
-- Combines staging emotion data for cross-source comparison

WITH ranked_emotions AS (
    SELECT
        source,
        dominant_emotion,
        word_count,
        char_length,
        COUNT(*) AS emotion_count
    FROM {{ ref('stg_emotions') }}
    GROUP BY source, dominant_emotion, word_count, char_length
)

SELECT
    source,
    dominant_emotion,
    COUNT(*) AS document_count,
    ROUND(AVG(word_count), 1) AS avg_word_count,
    ROUND(AVG(char_length), 1) AS avg_char_count,
    SUM(emotion_count) AS total_emotion_records
FROM ranked_emotions
GROUP BY source, dominant_emotion
