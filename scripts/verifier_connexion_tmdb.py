import os
from typing import Any

import requests
from dotenv import load_dotenv


URL_BASE_TMDB = "https://api.themoviedb.org/3"
DELAI_MAX_REQUETE = 10                       # Empêche une requête de rester bloquée


def valider_token(token: str | None) -> str:
    """Vérifie que le token TMDb existe et retire les espaces inutiles."""
    if not token or not token.strip():
        raise ValueError("Le token TMDb est absent du fichier .env.")

    return token.strip()


def charger_token_tmdb() -> str:
    """Charge et renvoie le token TMDb enregistré dans le fichier .env."""
    load_dotenv()

    return valider_token(os.getenv("TMDB_TOKEN"))


def creer_entetes(token: str) -> dict[str, str]:
    """Construit les en-têtes nécessaires à l'authentification TMDb."""
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


def requete_tmdb(
    endpoint: str,
    parametres: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Interroge un endpoint TMDb et renvoie sa réponse JSON."""
    token = charger_token_tmdb()
    entetes = creer_entetes(token)

    reponse = requests.get(
        f"{URL_BASE_TMDB}{endpoint}",
        headers=entetes,
        params=parametres,
        timeout=DELAI_MAX_REQUETE,
    )

    reponse.raise_for_status()

    return reponse.json()


def verifier_connexion() -> bool:
    """Vérifie que TMDb accepte le token configuré."""
    donnees = requete_tmdb("/authentication")

    return donnees.get("success", False)


def main() -> None:
    """Lance le contrôle de connexion à TMDb."""
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


if __name__ == "__main__":
    main()