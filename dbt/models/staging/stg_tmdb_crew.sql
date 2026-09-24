WITH source AS (
    SELECT *
    FROM {{ source('cinematch_landing', 'tmdb_films') }}
),
unnested AS (
    SELECT
        CAST(source.id AS INT64) AS tmdb_id,
        CAST(person.id AS INT64) AS person_id,
        TRIM(person.name) AS person_name,
        TRIM(person.original_name) AS original_name,
        TRIM(person.department) AS department,
        TRIM(person.job) AS job,
        TRIM(person.known_for_department) AS known_for_department,
        CAST(person.popularity AS FLOAT64) AS person_popularity,
        person.profile_path
    FROM source,
    UNNEST(source.credits.crew) AS person
)
SELECT *
FROM unnested