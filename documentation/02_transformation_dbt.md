# Transformation des données avec dbt

## Objectif

dbt est utilisé pour transformer les tables chargées dans BigQuery en tables plus propres et plus faciles à utiliser pour l'analyse, Power BI et la recommandation.

Les données sources restent dans le dataset `cinematch_landing`.  
Les modèles dbt sont créés dans `cinematch_dbt`.

## Organisation

### Staging

Les modèles de staging nettoient et standardisent les données sans trop s'éloigner des sources.

Principaux modèles :

- `stg_movielens_movies` : catalogue MovieLens ;
- `stg_movielens_links` : correspondances MovieLens, IMDb et TMDb ;
- `stg_movielens_ratings` : notes utilisateurs ;
- `stg_movielens_tags` : tags utilisateurs ;
- `stg_tmdb_films` : informations principales des films ;
- `stg_tmdb_genres` : genres ;
- `stg_tmdb_keywords` : mots-clés ;
- `stg_tmdb_cast` : casting ;
- `stg_tmdb_crew` : équipe technique.

Les champs imbriqués de TMDb sont séparés avec `UNNEST`.

### Marts

Les marts regroupent les données utiles pour l'analyse.

- `dim_films` : une ligne par film enrichi ;
- `dim_genres` : une ligne par genre ;
- `bridge_film_genres` : liaison entre films et genres ;
- `fct_ratings` : une ligne par note utilisateur ;
- `mart_film_metrics` : indicateurs par film.

## Contrôles

Les principaux tests dbt utilisés sont :

- `not_null` ;
- `unique` ;
- `relationships`.

Ils permettent de vérifier les identifiants, les doublons et la cohérence entre les tables.

Le build complet du projet se termine avec :

```text
PASS=74
WARN=0
ERROR=0
SKIP=0
```

## Résultat

La couche dbt permet maintenant de relier MovieLens et TMDb grâce aux identifiants des films et fournit des tables prêtes pour la suite du projet.

La prochaine étape est la création du tableau de bord Power BI.
