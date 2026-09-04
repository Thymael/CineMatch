# Collecte des données de CineMatch

## Objectif

Cette première collecte permet de construire un échantillon de films suffisamment complet pour tester le pipeline CineMatch avant son passage à une plus grande échelle.

Les données proviennent de MovieLens et de l'API TMDb.

## Sources utilisées

### MovieLens Latest Small

MovieLens fournit les données nécessaires au futur système de recommandation :

- `movies.csv` : catalogue des films et genres ;
- `ratings.csv` : notes attribuées par les utilisateurs ;
- `links.csv` : correspondances avec IMDb et TMDb ;
- `tags.csv` : mots-clés ajoutés par les utilisateurs.

Le dataset contient :

- 9 742 films ;
- 100 836 notes ;
- 610 utilisateurs anonymisés ;
- 3 683 tags.

Source : https://grouplens.org/datasets/movielens/

### TMDb

L'API TMDb complète MovieLens avec des informations descriptives :

- titre et résumé ;
- date de sortie ;
- genres ;
- durée ;
- affiche ;
- popularité et notes TMDb ;
- budget et recettes ;
- casting et équipe technique ;
- mots-clés ;
- identifiant IMDb.

Source : https://developer.themoviedb.org/

## Méthode de collecte

Les 100 films ayant reçu le plus de notes dans MovieLens ont été sélectionnés.

Le nombre de notes a été préféré à la meilleure moyenne afin d'éviter de sélectionner des films très bien notés par seulement quelques utilisateurs.

Le fichier `links.csv` permet ensuite de relier chaque `movieId` de MovieLens à son `tmdbId`.

Chaque film est demandé à l'API TMDb puis enregistré séparément au format JSON dans :

`data/raw/tmdb/`

Le script ignore les fichiers déjà présents. Une collecte interrompue peut donc reprendre sans télécharger une seconde fois les films déjà récupérés.

## Résultats

- films sélectionnés : 100 ;
- nouveaux films téléchargés : 95 ;
- films déjà présents : 5 ;
- erreurs API : 0 ;
- fichiers JSON obtenus : 100 ;
- identifiants TMDb uniques : 100.

## Contrôles réalisés

Les contrôles suivants ont été effectués :

- absence de doublons dans les `movieId` MovieLens ;
- notes comprises entre 0,5 et 5 ;
- présence de 100 fichiers JSON TMDb ;
- unicité des identifiants TMDb ;
- présence des crédits ;
- présence des mots-clés ;
- présence des identifiants IMDb ;
- reprise de la collecte sans nouveau téléchargement.

## Stockage

Les données brutes sont conservées localement pour le développement.

Le dossier `data/raw/` est exclu du dépôt GitHub. Les scripts sont publiés, mais pas les données téléchargées.

Dans la prochaine étape, les données brutes seront déposées dans un bucket privé Google Cloud Storage.

## Limites actuelles

Cette première version utilise seulement les 100 films les plus évalués.

Cet échantillon est adapté aux tests du pipeline, mais il favorise les films populaires et ne représente pas tout le catalogue MovieLens.

Une fois le pipeline validé, la collecte pourra être étendue à davantage de films.