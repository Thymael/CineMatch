from pathlib import Path
from zipfile import BadZipFile, ZipFile

import requests


URL_MOVIELENS = "https://www.kaggle.com/api/v1/datasets/download/grouplens/movielens-latest-small"
DOSSIER_SORTIE = Path("data/raw/movielens/ml-latest-small")
CHEMIN_ZIP = DOSSIER_SORTIE.parent / "ml-latest-small.zip"
DELAI_MAX = 60                                                        # Temps maximal de téléchargement


def telecharger_archive():
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)                  # Crée le dossier local

    reponse = requests.get(URL_MOVIELENS, timeout=DELAI_MAX)
    reponse.raise_for_status()

    CHEMIN_ZIP.write_bytes(reponse.content)                            # Conserve le ZIP original

    return CHEMIN_ZIP


def extraire_archive():
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)       # Crée le dossier de destination

    with ZipFile(CHEMIN_ZIP, "r") as archive:
        archive.extractall(DOSSIER_SORTIE)                  # Extrait les fichiers CSV                        # Extrait les fichiers CSV


if __name__ == "__main__":
    try:
        chemin = telecharger_archive()
        extraire_archive()

        taille_mo = chemin.stat().st_size / 1024 ** 2

        print(f"✅ MovieLens téléchargé : {taille_mo:.2f} Mo")
        print(f"📁 Dossier : {DOSSIER_SORTIE}")

    except (requests.exceptions.RequestException, BadZipFile) as erreur:
        print(f"❌ Téléchargement impossible : {erreur}")
        raise SystemExit(1)