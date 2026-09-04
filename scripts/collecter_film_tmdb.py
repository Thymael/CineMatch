import json
import time
from pathlib import Path

import pandas as pd
import requests

from scripts.verifier_connexion_tmdb import requete_tmdb


DOSSIER_MOVIELENS = Path("data/raw/movielens/ml-latest-small")
DOSSIER_SORTIE = Path("data/raw/tmdb")
NOMBRE_FILMS = 100
PAUSE_ENTRE_REQUETES = 0.2                                      # Évite d'envoyer trop de requêtes


def selectionner_films(nombre_films):
    notes = pd.read_csv(DOSSIER_MOVIELENS / "ratings.csv")      # Notes des utilisateurs
    liens = pd.read_csv(DOSSIER_MOVIELENS / "links.csv")        # Correspondances avec TMDb
    films = pd.read_csv(DOSSIER_MOVIELENS / "movies.csv")       # Titres des films

    popularite = (
        notes.groupby("movieId")
        .size()
        .reset_index(name="nombre_notes")
    )

    selection = (
        popularite
        .merge(liens, on="movieId", how="left")                 # Ajoute le tmdbId
        .merge(films[["movieId", "title"]], on="movieId")       # Ajoute le titre
        .dropna(subset=["tmdbId"])                              # Retire les identifiants manquants
        .sort_values("nombre_notes", ascending=False)           # Classe les films les plus évalués
        .head(nombre_films)
        .copy()
    )

    selection["tmdbId"] = selection["tmdbId"].astype(int)       # Transforme 862.0 en 862

    return selection


def recuperer_film(film_id):
    parametres = {
        "language": "fr-FR",
        "append_to_response": "credits,keywords,external_ids"
    }

    return requete_tmdb(f"/movie/{film_id}", parametres)


def construire_chemin(film_id):
    return DOSSIER_SORTIE / f"film_{film_id}.json"


def enregistrer_film(film):
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)            # Crée le dossier si nécessaire
    chemin_fichier = construire_chemin(film["id"])

    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(film, fichier, ensure_ascii=False, indent=2)   # Enregistre la réponse brute

    return chemin_fichier


if __name__ == "__main__":
    films_selectionnes = selectionner_films(NOMBRE_FILMS)

    films_recuperes = 0
    films_deja_presents = 0
    erreurs = 0

    print(f"\n🎬 Films sélectionnés : {len(films_selectionnes)}")

    for numero, (_, ligne) in enumerate(films_selectionnes.iterrows(), start=1):
        film_id = int(ligne["tmdbId"])
        titre_movielens = ligne["title"]
        chemin = construire_chemin(film_id)

        if chemin.exists():
            films_deja_presents += 1
            print(f"⏭️ [{numero}/{len(films_selectionnes)}] {titre_movielens} déjà présent")
            continue

        try:
            film = recuperer_film(film_id)
            chemin = enregistrer_film(film)
            films_recuperes += 1

            print(f"✅ [{numero}/{len(films_selectionnes)}] {film['title']} enregistré")

        except (ValueError, requests.exceptions.RequestException) as erreur:
            erreurs += 1
            print(f"❌ [{numero}/{len(films_selectionnes)}] {titre_movielens} : {erreur}")

        time.sleep(PAUSE_ENTRE_REQUETES)                         # Petite pause avant le film suivant

    print("\n📊 BILAN DE LA COLLECTE")
    print(f"Nouveaux films : {films_recuperes}")
    print(f"Films déjà présents : {films_deja_presents}")
    print(f"Erreurs : {erreurs}")

    if erreurs > 0:
        raise SystemExit(1)