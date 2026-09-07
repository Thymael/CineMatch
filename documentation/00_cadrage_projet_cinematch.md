# CinéMatch — Cadrage du projet

## 1. Présentation

CinéMatch est un projet data consacré aux films. Il doit permettre de réviser les compétences
attendues pour la certification tout en créant un projet complet à présenter dans un portfolio.

Le projet partira d'un premier prototype déjà réalisé avec l'API TMDb. Ce prototype permet de
rechercher un film, de choisir le bon résultat et d'afficher une fiche avec son affiche, son résumé,
ses genres, ses pays de production et ses principaux acteurs.

## 2. Problématique

> Comment exploiter plusieurs sources de données cinématographiques pour analyser les films et
> recommander à un utilisateur des œuvres susceptibles de lui plaire ?

## 3. Objectifs pédagogiques

Le projet doit permettre de travailler les compétences suivantes :

- interroger une API avec Python ;
- collecter et nettoyer des données ;
- stocker les fichiers bruts sans les modifier ;
- charger les données dans Google Cloud Storage et BigQuery ;
- transformer et tester les tables avec dbt ;
- réaliser une analyse exploratoire avec Python ;
- construire un tableau de bord Power BI ;
- créer un système simple de recommandation ;
- automatiser l'actualisation avec GitHub Actions ;
- documenter les choix, les limites et le fonctionnement du projet.

## 4. Périmètre du MVP

La première version portera uniquement sur les films.

### Sources principales

| Source | Rôle dans le projet |
|---|---|
| TMDb | Fiches des films, genres, casting, équipes, affiches, popularité et avis utilisateurs |
| MovieLens | Notes attribuées par des utilisateurs pour construire les recommandations |
| OMDb | Scores IMDb, Rotten Tomatoes et Metacritic lorsqu'ils sont disponibles |

### Sources bonus

| Source | Rôle dans le projet |
|---|---|
| Spotify | Bande originale ou album associé au film |
| New York Times | Résumé et lien vers une critique professionnelle |

Les séries, Spotify et les critiques professionnelles seront ajoutés uniquement après validation
du pipeline principal.

## 5. Livrables prévus

- scripts Python de collecte et de préparation ;
- fichiers bruts conservés au format JSON, CSV ou Parquet ;
- stockage GCS et tables BigQuery ;
- projet dbt avec modèles, tests et documentation ;
- notebook d'analyse exploratoire ;
- tableau de bord Power BI ;
- moteur de recommandation ;
- application Streamlit ;
- workflow GitHub Actions ;
- README et documentation technique.

## 6. Méthode de travail et clean code

Chaque étape du projet suivra la même organisation :

1. expliquer simplement l'objectif ;
2. modifier un petit nombre de fichiers ;
3. vérifier que le comportement reste correct ;
4. contrôler les données produites ;
5. mettre à jour la documentation ;
6. valider l'étape avant de continuer.

### Règles d'écriture du code

Le projet appliquera les règles suivantes :

- les variables auront des noms explicites ;
- les fonctions commenceront par un verbe ;
- chaque fonction aura une seule responsabilité ;
- les traitements répétés seront regroupés dans une fonction ;
- les valeurs importantes seront placées dans des constantes ;
- les fonctions réutilisables auront une docstring et des annotations de types simples ;
- les commentaires expliqueront un choix ou un cas particulier, pas une ligne évidente ;
- le code inutilisé ou commenté sera supprimé ;
- les secrets et les données locales ne seront jamais publiés sur GitHub.

Les commentaires courts pourront être placés à droite du code lorsqu'ils restent lisibles.
Les explications plus longues seront placées au-dessus du bloc concerné.

### Méthode de refactorisation

Avant de refactoriser un script :

1. exécuter le script et noter son résultat ;
2. effectuer les modifications sans ajouter de nouvelle fonctionnalité ;
3. vérifier la syntaxe avec `py_compile` ;
4. relancer les tests automatisés ;
5. réexécuter le script ;
6. comparer le nouveau résultat avec le résultat de référence.

Une refactorisation est validée uniquement si le comportement et les données obtenues
restent identiques.

## 7. Tests à prévoir dès le début

| Partie | Contrôles principaux |
|---|---|
| API | clé présente, statut HTTP, délai maximum, réponse JSON, pagination et erreur réseau |
| Données | identifiants non nuls, absence de doublons, types, dates, valeurs manquantes et volumes |
| Croisements | correspondance entre `movie_id`, `tmdb_id` et `imdb_id` |
| Stockage | fichier créé, schéma attendu, nombre de lignes et absence de perte |
| dbt | `unique`, `not_null`, relations, valeurs acceptées et tests métier |
| ML | séparation des données, comparaison avec une baseline et évaluation compréhensible |
| Application | film absent, affiche absente, résumé absent et recommandation impossible |

## 8. Étapes du projet

1. Cadrer le projet et fixer le MVP.
2. Créer le dépôt, l'arborescence et l'environnement Python.
3. Transformer le prototype en une collecte TMDb testable.
4. Ajouter MovieLens et fiabiliser les correspondances d'identifiants.
5. Conserver les données brutes et les envoyer dans GCS.
6. Charger les données dans BigQuery.
7. Construire les modèles et les tests dbt.
8. Réaliser l'EDA et le tableau de bord Power BI.
9. Construire une baseline puis les modèles de recommandation.
10. Créer l'application Streamlit.
11. Ajouter OMDb, Spotify et les critiques en extensions.
12. Automatiser, documenter et préparer la présentation du portfolio.

## 9. Critères de réussite du MVP

Le MVP sera considéré comme terminé lorsque :

- les films et les notes MovieLens pourront être reliés grâce à leurs identifiants ;
- les données brutes seront conservées et rechargeables ;
- BigQuery contiendra des tables propres construites avec dbt ;
- les principaux contrôles de qualité seront automatisés ;
- une EDA et un tableau de bord répondront à des questions métier claires ;
- le projet proposera des films similaires et des recommandations personnalisées simples ;
- une autre personne pourra comprendre et relancer le projet grâce au README.

## 10. Première décision

Le nom de travail est **CinéMatch**. Le projet commence avec **TMDb et MovieLens**. OMDb sera le
premier enrichissement, puis Spotify et les critiques professionnelles seront traités comme des bonus.
