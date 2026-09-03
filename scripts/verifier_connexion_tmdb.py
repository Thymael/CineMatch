import os

import requests
from dotenv import load_dotenv


URL_AUTHENTIFICATION = "https://api.themoviedb.org/3/authentication"
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


def verifier_connexion():
    load_dotenv()                                                       # Charge les variables de .env
    token = valider_token(os.getenv("TMDB_TOKEN"))                      # Récupère et contrôle le token
    entetes = creer_entetes(token)                                      # Prépare l'autorisation TMDb

    reponse = requests.get(
        URL_AUTHENTIFICATION,
        headers=entetes,
        timeout=DELAI_MAX
    )

    reponse.raise_for_status()                                          # Déclenche une erreur HTTP si nécessaire
    donnees = reponse.json()

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