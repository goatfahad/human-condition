-- Staging: emotion analysis results flattened
-- Sources: {{ ref('emotions_raw') }}

SELECT
    source,
    title,
    text,
    dominant_emotion,
    emotion_scores,
    LENGTH(text) AS char_length,
    ARRAY_LENGTH(STRING_SPLIT(text, ' ')) AS word_count
FROM {{ ref('emotions_raw') }}
