import json
from pathlib import Path

import requests

from scripts.verifier_connexion_tmdb import requete_tmdb


FILMS_IDS = [
    550,                                                               # Fight Club
    13,                                                                # Forrest Gump
    680,                                                               # Pulp Fiction
    155,                                                               # The Dark Knight
    27205                                                              # Inception
]                                      
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
    films_recuperes = 0

    for film_id in FILMS_IDS:
        try:
            film = recuperer_film(film_id)
            chemin = enregistrer_film(film)
            films_recuperes += 1

            print(f"✅ {film['title']} enregistré dans {chemin}")

        except (ValueError, requests.exceptions.RequestException) as erreur:
            print(f"❌ Film {film_id} non récupéré : {erreur}")

    print(f"\n🎬 Collecte terminée : {films_recuperes}/{len(FILMS_IDS)} films.")

    if films_recuperes != len(FILMS_IDS):
        raise SystemExit(1)