WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'movielens_ratings') }}
),
renamed AS (
    SELECT
        CAST (userId AS INT64) AS user_id,
        CAST (movieId AS INT64) AS movie_id,
        CAST (rating AS FLOAT64) AS rating,
        timestamp_seconds(CAST (timestamp AS INT64)) AS rated_at
    FROM source
)
SELECT *
FROM renamed