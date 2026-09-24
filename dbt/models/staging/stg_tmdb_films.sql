WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'tmdb_films') }}
),
renamed AS (
    SELECT
        CAST(id AS INT64) AS tmdb_id,
        CAST(imdb_id AS STRING) AS imdb_id,
        TRIM(title) AS title,
        TRIM(original_title) AS original_title,
        TRIM(overview) AS overview,
        TRIM(tagline) AS tagline,
        TRIM(original_language) AS original_language,
        release_date,
        CAST(runtime AS INT64) AS runtime,
        CAST(budget AS INT64) AS budget,
        CAST(revenue AS INT64) AS revenue,
        CAST(popularity AS FLOAT64) AS popularity,
        CAST(vote_average AS FLOAT64) AS vote_average,
        CAST(vote_count AS INT64) AS vote_count,
        TRIM(status) AS status,
        CAST(adult AS BOOL) AS adult,
        CAST(video AS BOOL) AS video,
        poster_path,
        backdrop_path,
        homepage,
        CAST(belongs_to_collection.id AS INT64) AS collection_id,
        TRIM(belongs_to_collection.name) AS collection_name
    FROM source
)
SELECT *
FROM renamed