import os

import requests
from dotenv import load_dotenv


URL_BASE = "https://api.themoviedb.org/3"
DELAI_MAX = 10                                                        # Évite une requête bloquée


def valider_token(token):
    if not token or not token.strip():
        raise ValueError("Le token TMDb est absent du fichier .env.")

    return token.strip()


def creer_entetes(token):
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

def requete_tmdb(endpoint, params=None):
    load_dotenv()                                                       # Charge le fichier .env
    token = valider_token(os.getenv("TMDB_TOKEN"))                      # Récupère le token
    entetes = creer_entetes(token)                                      # Prépare l'autorisation

    reponse = requests.get(
        f"{URL_BASE}{endpoint}",
        headers=entetes,
        params=params,
        timeout=DELAI_MAX
    )

    reponse.raise_for_status()                                          # Contrôle la réponse HTTP

    return reponse.json()

def verifier_connexion():
    donnees = requete_tmdb("/authentication")                           # Utilise la fonction générale

    return donnees.get("success", False)


if __name__ == "__main__":
    try:
        if verifier_connexion():
            print("✅ Connexion à TMDb réussie.")
        else:
            print("❌ TMDb n'a pas validé le token.")
            raise SystemExit(1)

    except ValueError as erreur:
        print(f"❌ Configuration incorrecte : {erreur}")
        raise SystemExit(1)

    except requests.exceptions.RequestException as erreur:
        print(f"❌ Requête TMDb impossible : {erreur}")
        raise SystemExit(1)