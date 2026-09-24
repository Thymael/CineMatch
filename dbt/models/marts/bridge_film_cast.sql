WITH films AS (
    SELECT
        movie_id,
        tmdb_id
    FROM {{ ref('dim_films') }}
),

cast_data AS (
    SELECT *
    FROM {{ ref('stg_tmdb_cast') }}
),

final AS (
    SELECT
        films.movie_id,
        cast_data.person_id,
        cast_data.person_name,
        cast_data.original_name,
        cast_data.character_name,
        cast_data.cast_order,
        cast_data.known_for_department,
        cast_data.person_popularity,
        cast_data.profile_path,
        CASE
            WHEN cast_data.profile_path IS NOT NULL
                THEN CONCAT('https://image.tmdb.org/t/p/w185', cast_data.profile_path)
        END AS profile_url
    FROM films
    INNER JOIN cast_data
        ON films.tmdb_id = cast_data.tmdb_id
)

SELECT *
FROM final