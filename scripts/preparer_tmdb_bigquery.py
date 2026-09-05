import json
from pathlib import Path


DOSSIER_ENTREE = Path("data/raw/tmdb")                         # Fichiers JSON bruts
DOSSIER_SORTIE = Path("data/processed/tmdb")                   # Fichiers préparés
FICHIER_SORTIE = DOSSIER_SORTIE / "films_tmdb.ndjson"          # Fichier pour BigQuery


def preparer_fichier():
    fichiers_json = sorted(DOSSIER_ENTREE.glob("film_*.json")) # Recherche les films

    if not fichiers_json:
        raise FileNotFoundError("Aucun fichier TMDb trouvé.")

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)           # Crée le dossier
    identifiants = set()                                       # Détecte les doublons

    with FICHIER_SORTIE.open("w", encoding="utf-8") as sortie:
        for chemin_film in fichiers_json:
            with chemin_film.open("r", encoding="utf-8") as entree:
                film = json.load(entree)                       # Lit le fichier brut

            film_id = film.get("id")

            if film_id is None:
                raise ValueError(f"ID absent dans {chemin_film}")

            if film_id in identifiants:
                raise ValueError(f"Film en double : {film_id}")

            identifiants.add(film_id)
            ligne_json = json.dumps(film, ensure_ascii=False)  # Place le film sur une ligne
            sortie.write(f"{ligne_json}\n")

    return len(fichiers_json)


if __name__ == "__main__":
    try:
        nombre_films = preparer_fichier()
        taille_mo = FICHIER_SORTIE.stat().st_size / 1_048_576

        print(f"✅ Fichier préparé : {FICHIER_SORTIE}")
        print(f"🎬 Films : {nombre_films}")
        print(f"📦 Taille : {taille_mo:.2f} Mo")

    except (OSError, ValueError) as erreur:
        print(f"❌ Préparation impossible : {erreur}")
        raise SystemExit(1)