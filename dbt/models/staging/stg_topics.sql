-- Staging: topic modeling results
-- Sources: {{ ref('topics_raw') }}

SELECT
    Topic,
    Name,
    Count,
    Representation,
    Rep
FROM {{ ref('topics_raw') }}
