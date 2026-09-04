from pathlib import Path

import pandas as pd


DOSSIER_MOVIELENS = Path("data/raw/movielens/ml-latest-small")


def charger_donnees():
    films = pd.read_csv(DOSSIER_MOVIELENS / "movies.csv")       # Catalogue des films
    notes = pd.read_csv(DOSSIER_MOVIELENS / "ratings.csv")      # Notes des utilisateurs
    liens = pd.read_csv(DOSSIER_MOVIELENS / "links.csv")        # Liens vers IMDb et TMDb
    tags = pd.read_csv(DOSSIER_MOVIELENS / "tags.csv")          # Mots-clés des utilisateurs

    return films, notes, liens, tags


def afficher_resume(films, notes, liens, tags):
    print("\n🎬 RÉSUMÉ DU DATASET MOVIELENS")
    print(f"Films : {len(films):,}")                            # Nombre de films
    print(f"Notes : {len(notes):,}")                            # Nombre total de notes
    print(f"Utilisateurs : {notes['userId'].nunique():,}")       # Utilisateurs différents
    print(f"Tags : {len(tags):,}")                              # Nombre total de tags
    print(f"Note minimale : {notes['rating'].min()}")
    print(f"Note maximale : {notes['rating'].max()}")
    print(f"Note moyenne : {notes['rating'].mean():.2f}")

    print("\n🔗 IDENTIFIANTS EXTERNES")
    print(f"Identifiants IMDb manquants : {liens['imdbId'].isna().sum()}")
    print(f"Identifiants TMDb manquants : {liens['tmdbId'].isna().sum()}")

    print("\n📋 PREMIERS FILMS")
    print(films.head())


def verifier_donnees(films, notes):
    doublons_films = films["movieId"].duplicated().sum()        # Cherche les movieId répétés
    notes_invalides = (~notes["rating"].between(0.5, 5)).sum()  # Cherche les notes hors limites

    print("\n🔎 CONTRÔLES")
    print(f"movieId en double : {doublons_films}")
    print(f"Notes invalides : {notes_invalides}")

    if doublons_films == 0 and notes_invalides == 0:
        print("✅ Les contrôles principaux sont réussis.")
    else:
        print("⚠️ Certaines données doivent être vérifiées.")


if __name__ == "__main__":
    films, notes, liens, tags = charger_donnees()
    afficher_resume(films, notes, liens, tags)
    verifier_donnees(films, notes)