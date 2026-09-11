from pathlib import Path
from zipfile import BadZipFile, ZipFile

import requests


URL_MOVIELENS = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "grouplens/movielens-latest-small"
)
DOSSIER_SORTIE = Path("data/raw/movielens/ml-latest-small")
CHEMIN_ZIP = DOSSIER_SORTIE.parent / "ml-latest-small.zip"
DELAI_MAX_REQUETE = 60


def telecharger_archive() -> Path:
    """Télécharge l'archive MovieLens et renvoie son chemin local."""
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

    reponse = requests.get(
        URL_MOVIELENS,
        timeout=DELAI_MAX_REQUETE,
    )
    reponse.raise_for_status()

    CHEMIN_ZIP.write_bytes(reponse.content)

    return CHEMIN_ZIP


def extraire_archive() -> None:
    """Extrait les fichiers MovieLens dans le dossier prévu."""
    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

    with ZipFile(CHEMIN_ZIP, "r") as archive:
        archive.extractall(DOSSIER_SORTIE)


def main() -> None:
    """Télécharge et extrait le dataset MovieLens."""
    try:
        chemin_archive = telecharger_archive()
        extraire_archive()

        taille_mo = chemin_archive.stat().st_size / 1024**2

        print(f"✅ MovieLens téléchargé : {taille_mo:.2f} Mo")
        print(f"📁 Dossier : {DOSSIER_SORTIE}")

    except (requests.exceptions.RequestException, BadZipFile) as erreur:
        print(f"❌ Téléchargement impossible : {erreur}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()