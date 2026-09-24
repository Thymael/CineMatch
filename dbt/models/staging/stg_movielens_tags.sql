WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'movielens_tags') }}
),
renamed AS (
    SELECT
        CAST (userId AS INT64) AS user_id,
        CAST (movieId AS INT64) AS movie_id,
        TRIM(tag) AS tag,
        timestamp_seconds(CAST (timestamp AS INT64)) AS tagged_at
    FROM source
)
SELECT *
FROM renamed