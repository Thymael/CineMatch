# CinéMatch

CinéMatch est un projet data consacré à l'analyse de films et à la recommandation
personnalisée.

## Objectif

Croiser plusieurs sources cinématographiques afin de construire un pipeline de données,
réaliser une analyse exploratoire et recommander des films à un utilisateur.

## Pipeline

```text
TMDb + MovieLens → Python → GCS → BigQuery → dbt → EDA et ML → Power BI et Streamlit
```

## Sources de données

- **MovieLens Latest Small** : 9 742 films et 100 836 notes utilisateurs ;
- **TMDb** : fiches détaillées de 100 films pour le prototype ;
- **OMDb, Spotify et New York Times** : enrichissements prévus ultérieurement.

## Installation

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Ajouter ensuite le token TMDb dans le fichier `.env` :

```text
TMDB_TOKEN=mon_token
```

## Exécution

Les commandes doivent être lancées depuis la racine du projet :

```bash
python -m scripts.telecharger_movielens
python -m scripts.verifier_donnees_movielens
python -m scripts.verifier_connexion_tmdb
python -m scripts.collecter_film_tmdb
python -m scripts.preparer_tmdb_bigquery
python -m pytest -q
```

## Avancement

- [x] Collecte MovieLens et TMDb
- [x] Stockage dans Google Cloud Storage
- [x] Chargement et contrôle dans BigQuery
- [x] Transformation avec dbt
- [ ] Analyse exploratoire et Power BI
- [ ] Modèles de recommandation
- [ ] Application Streamlit

## Documentation

- [Cadrage du projet](documentation/00_cadrage_projet_cinematch.md)
- [Collecte et stockage des données](documentation/01_collecte_donnees.md)
- [Transformation avec dbt](documentation/02_transformation_dbt.md)