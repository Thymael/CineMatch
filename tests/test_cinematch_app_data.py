import pandas as pd

import pytest

from app.data import (
    filtrer_catalogue,
    meilleurs_par_genre,
    recommander_selon_favoris,
)


def catalogue_exemple() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"content_type": "movie", "genres": "Action, Drame", "rating_average": 8.0},
            {"content_type": "tv", "genres": "Drame", "rating_average": 7.0},
            {"content_type": "tv", "genres": "Comédie", "rating_average": 6.0},
        ]
    )


def test_filtre_type_genre_et_note() -> None:
    resultat = filtrer_catalogue(catalogue_exemple(), "Séries", ["Drame"], 6.5)

    assert len(resultat) == 1
    assert resultat.iloc[0]["content_type"] == "tv"


def test_filtre_tous_conserve_le_catalogue() -> None:
    resultat = filtrer_catalogue(catalogue_exemple(), "Tous", [], 0.0)

    assert len(resultat) == 3


def test_genre_est_compare_comme_une_valeur_exacte() -> None:
    resultat = filtrer_catalogue(catalogue_exemple(), "Tous", ["Action.*"], 0.0)

    assert resultat.empty


def test_type_inconnu_est_refuse() -> None:
    with pytest.raises(ValueError, match="Type de contenu inconnu"):
        filtrer_catalogue(catalogue_exemple(), "Documentaires", [], 0.0)


def test_recommandations_personnelles_additionnent_les_scores() -> None:
    catalogue = pd.DataFrame(
        [
            {"content_key": "movie:1", "title": "A"},
            {"content_key": "movie:2", "title": "B"},
            {"content_key": "tv:3", "title": "C"},
        ]
    )
    recommandations = pd.DataFrame(
        [
            {"source_content_key": "movie:1", "recommended_content_key": "tv:3", "similarity_score": 0.4},
            {"source_content_key": "movie:2", "recommended_content_key": "tv:3", "similarity_score": 0.5},
        ]
    )

    resultat = recommander_selon_favoris(
        ["movie:1", "movie:2"],
        recommandations,
        catalogue,
    )

    assert resultat.iloc[0]["content_key"] == "tv:3"
    assert resultat.iloc[0]["score_personnel"] == pytest.approx(0.9)


def test_meilleurs_par_genre_respecte_le_minimum_de_votes() -> None:
    contenus = pd.DataFrame(
        [
            {
                "title": "Très bien mais peu vu",
                "genres": "Drame",
                "rating_average": 9.8,
                "rating_count": 20,
                "popularity": 2,
            },
            {
                "title": "Lauréat",
                "genres": "Drame, Thriller",
                "rating_average": 8.4,
                "rating_count": 500,
                "popularity": 10,
            },
            {
                "title": "Finaliste",
                "genres": "Drame",
                "rating_average": 8.1,
                "rating_count": 900,
                "popularity": 20,
            },
        ]
    )

    resultat = meilleurs_par_genre(contenus)

    assert resultat.set_index("genre").loc["Drame", "title"] == "Lauréat"
    assert resultat.set_index("genre").loc["Thriller", "title"] == "Lauréat"

