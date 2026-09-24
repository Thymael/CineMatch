WITH ratings AS (
    SELECT *
    FROM {{ ref('fct_ratings') }}
),

rating_metrics AS (
    SELECT
        movie_id,
        COUNT(*) AS rating_count,
        COUNT(DISTINCT user_id) AS user_count,
        AVG(rating) AS movielens_rating_average,
        MIN(rating) AS movielens_rating_min,
        MAX(rating) AS movielens_rating_max
    FROM ratings
    GROUP BY movie_id
),

films AS (
    SELECT *
    FROM {{ ref('dim_films') }}
),

final AS (
    SELECT
        films.movie_id,
        films.tmdb_id,
        films.imdb_id,
        films.title,
        films.original_title,
        films.release_date,
        films.release_year,
        films.runtime,
        films.budget,
        films.revenue,
        films.profit,
        CASE
            WHEN films.budget > 0 AND films.revenue > 0
                THEN SAFE_DIVIDE(films.profit, films.budget)
        END AS roi,
        films.popularity AS tmdb_popularity,
        films.vote_average AS tmdb_vote_average,
        films.vote_average / 2 AS tmdb_vote_average_5,
        films.vote_count AS tmdb_vote_count,
        rating_metrics.rating_count,
        rating_metrics.user_count,
        rating_metrics.movielens_rating_average,
        rating_metrics.movielens_rating_min,
        rating_metrics.movielens_rating_max,
        rating_metrics.movielens_rating_average - (films.vote_average / 2) AS rating_gap
    FROM films
    LEFT JOIN rating_metrics
        ON films.movie_id = rating_metrics.movie_id
)

SELECT *
FROM final