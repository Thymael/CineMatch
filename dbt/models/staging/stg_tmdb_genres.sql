WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'tmdb_films') }}
),
unnested AS (
    SELECT
        CAST(source.id AS INT64) AS tmdb_id,
        CAST(genre.id AS INT64) AS genre_id,
        TRIM(genre.name) AS genre_name
    FROM source,
    UNNEST(source.genres) AS genre
)
SELECT *
FROM unnested