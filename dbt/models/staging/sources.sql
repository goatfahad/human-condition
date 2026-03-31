-- Staging: raw corpus flattened from JSON lines
-- Sources: {{ ref('corpus_raw') }}

SELECT
    source,
    title,
    text,
    metadata,
    LENGTH(text) AS char_length,
    ARRAY_LENGTH(STRING_SPLIT(text, ' ')) AS word_count,
    {{ dbt.safe_cast("metadata", api.Column.translate_type("json")) }} AS metadata_parsed
FROM {{ ref('corpus_raw') }}
