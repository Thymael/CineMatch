WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'movielens_links') }}
),
renamed AS (
    SELECT
        CAST (movieId AS INT64) AS movie_id,
        CAST (imdbId AS STRING) AS imdb_id,
        CAST (tmdbId AS INT64) AS tmdb_id
    FROM source
)
SELECT *
FROM renamed