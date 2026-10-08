WITH ratings AS (
    SELECT *
    FROM {{ ref('stg_movielens_ratings') }}
),

links AS (
    SELECT *
    FROM {{ ref('stg_movielens_links') }}
),

films AS (
    SELECT
        movie_id,
        tmdb_id
    FROM {{ ref('dim_films') }}
),

movie_mapping AS (
    SELECT
        links.movie_id AS source_movie_id,
        films.movie_id AS canonical_movie_id

    FROM links

    INNER JOIN films
        ON links.tmdb_id = films.tmdb_id
),

ratings_remapped AS (
    SELECT
        ratings.user_id,
        movie_mapping.canonical_movie_id AS movie_id,
        ratings.rating,
        ratings.rated_at,

        ROW_NUMBER() OVER (
            PARTITION BY
                ratings.user_id,
                movie_mapping.canonical_movie_id

            ORDER BY ratings.rated_at DESC
        ) AS rang

    FROM ratings

    INNER JOIN movie_mapping
        ON ratings.movie_id = movie_mapping.source_movie_id
)

SELECT
    user_id,
    movie_id,
    rating,
    rated_at

FROM ratings_remapped

WHERE rang = 1