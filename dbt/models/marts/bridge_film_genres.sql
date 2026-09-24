WITH films AS (
    SELECT
        movie_id,
        tmdb_id
    FROM {{ ref('dim_films') }}
),

genres AS (
    SELECT
        tmdb_id,
        genre_id
    FROM {{ ref('stg_tmdb_genres') }}
),

final AS (
    SELECT
        films.movie_id,
        genres.genre_id
    FROM films
    INNER JOIN genres
        ON films.tmdb_id = genres.tmdb_id
)

SELECT *
FROM final