import json
from pathlib import Path

import requests

from scripts.verifier_connexion_tmdb import requete_tmdb


FILM_ID = 550                                                         # Identifiant TMDb de Fight Club
DOSSIER_SORTIE = Path("data/raw/tmdb")


def recuperer_film(film_id):
    parametres = {
        "language": "fr-FR",
        "append_to_response": "credits,keywords,external_ids"
    }

    return requete_tmdb(f"/movie/{film_id}", parametres)


def enregistrer_film(film):
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)                  # Crée le dossier si nécessaire

    chemin_fichier = DOSSIER_SORTIE / f"film_{film['id']}.json"

    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(film, fichier, ensure_ascii=False, indent=2)          # Conserve la réponse brute en JSON

    return chemin_fichier


if __name__ == "__main__":
    try:
        film = recuperer_film(FILM_ID)
        chemin = enregistrer_film(film)

        print(f"🎬 Film récupéré : {film['title']}")
        print(f"💾 Fichier créé : {chemin}")

    except (ValueError, requests.exceptions.RequestException) as erreur:
        print(f"❌ Collecte impossible : {erreur}")
        raise SystemExit(1)