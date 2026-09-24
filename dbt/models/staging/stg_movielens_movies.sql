WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'movielens_movies') }}
),
renamed AS (
    SELECT
        CAST (movieId AS INT64) AS movie_id,
        TRIM(title) AS title,
        TRIM(genres) AS genres
    FROM source
)
SELECT *
FROM renamed