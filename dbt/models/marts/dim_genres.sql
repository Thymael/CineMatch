WITH genres AS (
    SELECT DISTINCT
        genre_id,
        genre_name
    FROM {{ ref('stg_tmdb_genres') }}
)

SELECT *
FROM genres