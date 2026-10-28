"""Accès aux données BigQuery utilisées par l'application Streamlit."""

from __future__ import annotations

import os
import re

import pandas as pd
from google.cloud import bigquery


PROJECT_ID = os.getenv("CINEMATCH_GCP_PROJECT", "cinematch-507613")
DATASET_ID = os.getenv("CINEMATCH_GOLD_DATASET", "cinematch_gold")
IDENTIFIANT_BIGQUERY = re.compile(r"^[A-Za-z0-9_-]+$")


def _table(name: str) -> str:
    """Retourne un identifiant BigQuery entièrement qualifié et validé."""
    if not all(
        IDENTIFIANT_BIGQUERY.fullmatch(value)
        for value in (PROJECT_ID, DATASET_ID, name)
    ):
        raise ValueError("Identifiant BigQuery invalide.")
    return f"`{PROJECT_ID}.{DATASET_ID}.{name}`"


def charger_catalogue() -> pd.DataFrame:
    """Charge le catalogue enrichi avec ses genres depuis BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)
    requete = f"""
        WITH genres AS (
            SELECT
                CONCAT('movie:', CAST(f.tmdb_id AS STRING)) AS content_key,
                STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
            FROM {_table('dim_films')} AS f
            INNER JOIN {_table('bridge_film_genres')} AS b USING (movie_id)
            INNER JOIN {_table('dim_genres')} AS g USING (genre_id)
            GROUP BY content_key

            UNION ALL

            SELECT
                CONCAT('tv:', CAST(b.series_id AS STRING)) AS content_key,
                STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
            FROM {_table('bridge_series_genres')} AS b
            INNER JOIN {_table('dim_genres')} AS g USING (genre_id)
            GROUP BY content_key
        )
        SELECT
            c.content_key,
            c.content_type,
            c.title,
            c.original_title,
            c.overview,
            c.start_year,
            c.runtime,
            c.number_of_seasons,
            c.number_of_episodes,
            c.popularity,
            c.rating_average,
            c.rating_count,
            c.status,
            c.poster_url,
            COALESCE(genres.genres, 'Non renseigné') AS genres
        FROM {_table('dim_catalogue')} AS c
        LEFT JOIN genres USING (content_key)
        ORDER BY c.popularity DESC
    """
    lignes = client.query(requete).result()
    return pd.DataFrame([dict(ligne.items()) for ligne in lignes])


def charger_recommandations() -> pd.DataFrame:
    """Charge les recommandations et les informations à afficher."""
    client = bigquery.Client(project=PROJECT_ID)
    requete = f"""
        SELECT
            recommandations.source_content_key,
            recommandations.recommended_content_key,
            recommandations.recommended_title,
            recommandations.recommended_content_type,
            recommandations.rank,
            recommandations.similarity_score,
            contenus.start_year,
            contenus.rating_average,
            contenus.poster_url
        FROM {_table('recommandations_contenu')} AS recommandations
        LEFT JOIN {_table('dim_catalogue')} AS contenus
            ON recommandations.recommended_content_key = contenus.content_key
        ORDER BY recommandations.source_content_key, recommandations.rank
    """
    lignes = client.query(requete).result()
    return pd.DataFrame([dict(ligne.items()) for ligne in lignes])


def charger_bandes_originales() -> pd.DataFrame:
    """Charge les bandes originales trouvées dans MusicBrainz."""
    client = bigquery.Client(project=PROJECT_ID)
    requete = f"""
        SELECT *
        FROM {_table('bandes_originales')}
    """
    lignes = client.query(requete).result()
    return pd.DataFrame([dict(ligne.items()) for ligne in lignes])


def charger_oscars_films() -> pd.DataFrame:
    """Charge les données nécessaires au palmarès des films."""
    client = bigquery.Client(project=PROJECT_ID)
    requete = f"""
        SELECT
            f.movie_id,
            f.title,
            f.release_date,
            f.runtime,
            f.budget,
            f.revenue,
            f.profit,
            SAFE_DIVIDE(f.profit, f.budget) AS roi,
            f.popularity,
            f.rating_average,
            f.rating_count,
            f.poster_url,
            STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
        FROM {_table('dim_films')} AS f
        LEFT JOIN {_table('bridge_film_genres')} AS b USING (movie_id)
        LEFT JOIN {_table('dim_genres')} AS g USING (genre_id)
        GROUP BY
            f.movie_id, f.title, f.release_date, f.runtime, f.budget,
            f.revenue, f.profit, f.popularity, f.rating_average,
            f.rating_count, f.poster_url
    """
    lignes = client.query(requete).result()
    return pd.DataFrame([dict(ligne.items()) for ligne in lignes])


def charger_oscars_series() -> pd.DataFrame:
    """Charge les données nécessaires au palmarès des séries."""
    client = bigquery.Client(project=PROJECT_ID)
    requete = f"""
        SELECT
            s.series_id,
            s.title,
            s.first_air_date,
            s.last_air_date,
            s.number_of_seasons,
            s.number_of_episodes,
            s.popularity,
            s.rating_average,
            s.rating_count,
            s.status,
            s.in_production,
            s.poster_url,
            DATE_DIFF(
                COALESCE(s.last_air_date, CURRENT_DATE()),
                s.first_air_date,
                DAY
            ) AS duration_days,
            STRING_AGG(DISTINCT g.genre_name, ', ' ORDER BY g.genre_name) AS genres
        FROM {_table('dim_series')} AS s
        LEFT JOIN {_table('bridge_series_genres')} AS b USING (series_id)
        LEFT JOIN {_table('dim_genres')} AS g USING (genre_id)
        GROUP BY
            s.series_id, s.title, s.first_air_date, s.last_air_date,
            s.number_of_seasons, s.number_of_episodes, s.popularity,
            s.rating_average, s.rating_count, s.status, s.in_production,
            s.poster_url
    """
    lignes = client.query(requete).result()
    return pd.DataFrame([dict(ligne.items()) for ligne in lignes])


def charger_profils_utilisateurs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge les profils ML et leurs films caractéristiques."""
    client = bigquery.Client(project=PROJECT_ID)
    profils = client.query(
        f"SELECT * FROM {_table('profil_segments')} ORDER BY segment_id"
    ).result()
    preferences = client.query(
        f"SELECT * FROM {_table('preferences_segments')} "
        "ORDER BY segment_id, rang"
    ).result()
    return (
        pd.DataFrame([dict(ligne.items()) for ligne in profils]),
        pd.DataFrame([dict(ligne.items()) for ligne in preferences]),
    )


def meilleurs_par_genre(
    contenus: pd.DataFrame,
    evaluations_minimum: int = 100,
) -> pd.DataFrame:
    """Garde l'œuvre la mieux notée de chaque genre avec assez d'évaluations."""
    eligibles = contenus[
        (contenus["rating_count"].fillna(0) >= evaluations_minimum)
        & contenus["rating_average"].notna()
        & contenus["genres"].notna()
    ].copy()
    if eligibles.empty:
        return eligibles.assign(genre=pd.Series(dtype="object"))

    eligibles["genre"] = eligibles["genres"].str.split(",")
    eligibles = eligibles.explode("genre")
    eligibles["genre"] = eligibles["genre"].str.strip()
    eligibles = eligibles[
        eligibles["genre"].notna()
        & (eligibles["genre"] != "")
        & (eligibles["genre"] != "Non renseigné")
    ]
    return (
        eligibles.sort_values(
            ["genre", "rating_average", "rating_count", "popularity"],
            ascending=[True, False, False, False],
        )
        .drop_duplicates("genre")
        .sort_values("genre")
        .reset_index(drop=True)
    )


def filtrer_catalogue(
    catalogue: pd.DataFrame,
    type_contenu: str,
    genres: list[str],
    note_minimale: float,
) -> pd.DataFrame:
    """Applique les filtres de l'interface sans modifier le catalogue source."""
    codes_types = {"Tous": None, "Films": "movie", "Séries": "tv"}
    if type_contenu not in codes_types:
        raise ValueError(f"Type de contenu inconnu : {type_contenu}")

    resultat = catalogue
    code_type = codes_types[type_contenu]
    if code_type is not None:
        resultat = resultat[resultat["content_type"] == code_type]

    if genres:
        genres_recherches = set(genres)
        resultat = resultat[
            resultat["genres"].fillna("").map(
                lambda valeur: bool(
                    genres_recherches.intersection(
                        genre.strip() for genre in valeur.split(",")
                    )
                )
            )
        ]

    return resultat[resultat["rating_average"].fillna(0) >= note_minimale].copy()


def recommander_selon_favoris(
    favoris: list[str],
    recommandations: pd.DataFrame,
    catalogue: pd.DataFrame,
    nombre: int = 5,
) -> pd.DataFrame:
    """Additionne les scores des favoris pour créer un profil personnel."""
    if not favoris:
        return pd.DataFrame()

    resultats = recommandations[
        recommandations["source_content_key"].isin(favoris)
        & recommandations["recommended_content_key"].isin(
            catalogue["content_key"]
        )
    ]
    scores = (
        resultats.groupby("recommended_content_key")["similarity_score"]
        .sum()
        .sort_values(ascending=False)
    )
    scores = scores[~scores.index.isin(favoris)].head(nombre)

    profil = scores.rename("score_personnel").reset_index()
    return profil.merge(
        catalogue,
        left_on="recommended_content_key",
        right_on="content_key",
        how="left",
    )

