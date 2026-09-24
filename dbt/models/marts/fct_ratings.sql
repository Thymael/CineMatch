WITH ratings AS (
    SELECT *
    FROM {{ ref('stg_movielens_ratings') }}
),

films AS (
    SELECT movie_id
    FROM {{ ref('dim_films') }}
),

filtered AS (
    SELECT
        ratings.user_id,
        ratings.movie_id,
        ratings.rating,
        ratings.rated_at
    FROM ratings
    INNER JOIN films
        ON ratings.movie_id = films.movie_id
)

SELECT *
FROM filtered