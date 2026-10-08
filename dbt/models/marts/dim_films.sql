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

rating_counts AS (
    SELECT
        movie_id,
        COUNT(*) AS rating_count
    FROM {{ ref('stg_movielens_ratings') }}
    GROUP BY movie_id
),

links_ranked AS (
    SELECT
        links.movie_id,
        links.imdb_id,
        links.tmdb_id,
        COALESCE(rating_counts.rating_count, 0) AS rating_count,

        ROW_NUMBER() OVER (
            PARTITION BY links.tmdb_id
            ORDER BY
                COALESCE(rating_counts.rating_count, 0) DESC,
                links.movie_id ASC
        ) AS rang

    FROM links

    LEFT JOIN rating_counts
        ON links.movie_id = rating_counts.movie_id

    WHERE links.tmdb_id IS NOT NULL
),

canonical_links AS (
    SELECT
        movie_id,
        imdb_id,
        tmdb_id
    FROM links_ranked
    WHERE rang = 1
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

        CASE
            WHEN tmdb.poster_path IS NOT NULL
                THEN CONCAT(
                    'https://image.tmdb.org/t/p/w500',
                    tmdb.poster_path
                )
        END AS poster_url,

        tmdb.backdrop_path,

        CASE
            WHEN tmdb.backdrop_path IS NOT NULL
                THEN CONCAT(
                    'https://image.tmdb.org/t/p/w780',
                    tmdb.backdrop_path
                )
        END AS backdrop_url,

        tmdb.homepage,
        tmdb.collection_id,
        tmdb.collection_name

    FROM tmdb

    INNER JOIN canonical_links
        ON tmdb.tmdb_id = canonical_links.tmdb_id

    INNER JOIN movies
        ON canonical_links.movie_id = movies.movie_id
)

SELECT *
FROM joined