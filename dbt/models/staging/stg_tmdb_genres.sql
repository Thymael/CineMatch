WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'tmdb_films') }}
),
unnested AS (
    SELECT
        CAST(id AS INT64) AS tmdb_id,
        CAST(genre.id AS INT64) AS genre_id,
        TRIM(genre.name) AS genre_name
    FROM source,
    UNNEST(genres) AS genre
)
SELECT *
FROM unnested