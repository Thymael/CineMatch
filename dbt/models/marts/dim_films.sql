WITH tmdb AS (
    SELECT *
    FROM {{ ref('stg_tmdb_films') }}
),

links AS (
    SELECT *
    FROM {{ ref('stg_movielens_links') }}
),

movies AS (
    SELECT *
    FROM {{ ref('stg_movielens_movies') }}
),

joined AS (
    SELECT
        movies.movie_id,
        tmdb.tmdb_id,
        tmdb.imdb_id,
        tmdb.title,
        tmdb.original_title,
        movies.genres AS movielens_genres,
        tmdb.overview,
        tmdb.tagline,
        tmdb.original_language,
        tmdb.release_date,
        EXTRACT(YEAR FROM tmdb.release_date) AS release_year,
        tmdb.runtime,
        tmdb.budget,
        tmdb.revenue,
        CASE
            WHEN tmdb.budget > 0 AND tmdb.revenue > 0
                THEN tmdb.revenue - tmdb.budget
        END AS profit,
        tmdb.popularity,
        tmdb.vote_average,
        tmdb.vote_count,
        tmdb.status,
        tmdb.adult,
        tmdb.video,
        tmdb.poster_path,
        tmdb.backdrop_path,
        tmdb.homepage,
        tmdb.collection_id,
        tmdb.collection_name
    FROM tmdb
    INNER JOIN links
        ON tmdb.tmdb_id = links.tmdb_id
    INNER JOIN movies
        ON links.movie_id = movies.movie_id
)

SELECT *
FROM joined