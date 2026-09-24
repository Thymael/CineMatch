WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'tmdb_films') }}
),
unnested AS (
    SELECT
        CAST(source.id AS INT64) AS tmdb_id,
        CAST(keyword.id AS INT64) AS keyword_id,
        TRIM(keyword.name) AS keyword_name
    FROM source,
    UNNEST(source.keywords.keywords) AS keyword
)
SELECT *
FROM unnested