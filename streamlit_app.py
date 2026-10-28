"""Application Streamlit du catalogue CinéMatch."""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from app.data import (
    charger_bandes_originales,
    charger_catalogue,
    charger_oscars_films,
    charger_oscars_series,
    charger_profils_utilisateurs,
    charger_recommandations,
    filtrer_catalogue,
    meilleurs_par_genre,
    recommander_selon_favoris,
)


BANNIERE = Path("assets/cinematch_awards_banner.png")
COULEURS_GENRES = [
    "#E3B65B", "#8F1D2C", "#557A95", "#698F62", "#C56E33",
    "#795879", "#F0D58A", "#6B2D3E", "#7A9E9F", "#B76E79",
    "#8C6A43", "#4F6D7A", "#A44A3F", "#7D8F69", "#D08C60",
]

st.set_page_config(page_title="CinéMatch", page_icon=":material/movie:", layout="wide")


@st.cache_data(ttl="10m", max_entries=2, show_spinner="Chargement du catalogue…")
def obtenir_catalogue() -> pd.DataFrame:
    return charger_catalogue()


@st.cache_data(ttl="10m", max_entries=2, show_spinner="Chargement des recommandations…")
def obtenir_recommandations() -> pd.DataFrame:
    return charger_recommandations()


@st.cache_data(ttl="10m", max_entries=2, show_spinner=False)
def obtenir_bandes_originales() -> pd.DataFrame:
    return charger_bandes_originales()


@st.cache_data(ttl="10m", max_entries=2, show_spinner=False)
def obtenir_oscars_films() -> pd.DataFrame:
    return charger_oscars_films()


@st.cache_data(ttl="10m", max_entries=2, show_spinner=False)
def obtenir_oscars_series() -> pd.DataFrame:
    return charger_oscars_series()


@st.cache_data(ttl="10m", max_entries=2, show_spinner=False)
def obtenir_profils_utilisateurs() -> tuple[pd.DataFrame, pd.DataFrame]:
    return charger_profils_utilisateurs()


def nom_contenu(cle: str, catalogue: pd.DataFrame) -> str:
    """Retourne le titre lisible associé à une clé de contenu."""
    ligne = catalogue[catalogue["content_key"] == cle]
    if ligne.empty:
        return cle
    contenu = ligne.iloc[0]
    type_lisible = "Film" if contenu["content_type"] == "movie" else "Série"
    annee = int(contenu["start_year"]) if pd.notna(contenu["start_year"]) else "?"
    return f"{contenu['title']} ({annee}) · {type_lisible}"


def gagnant(donnees: pd.DataFrame, colonne: str, maximum: bool = True):
    """Retourne la ligne gagnante d'une catégorie, ou None."""
    eligibles = donnees[donnees[colonne].notna()]
    if eligibles.empty:
        return None
    return eligibles.sort_values(
        [colonne, "rating_count"],
        ascending=[not maximum, False],
    ).iloc[0]


def afficher_prix(prix: list[tuple[str, object, str]]) -> None:
    """Affiche une grille simple de récompenses."""
    colonnes = st.columns(3)
    for index, (nom_prix, laureat, resultat) in enumerate(prix):
        with colonnes[index % 3]:
            with st.container(border=True):
                st.caption(nom_prix.upper())
                if laureat is None:
                    st.info("Donnée non disponible")
                    continue
                if pd.notna(laureat.get("poster_url")):
                    st.image(
                        laureat["poster_url"],
                        alt=f"Affiche de {laureat['title']}",
                    )
                st.subheader(laureat["title"])
                st.markdown(f"**{resultat}**")


def montant(valeur: float) -> str:
    """Formate un montant TMDb exprimé en dollars."""
    if valeur >= 1_000_000_000:
        return f"{valeur / 1_000_000_000:.2f} Md$"
    return f"{valeur / 1_000_000:.1f} M$"


def genre_principal(valeur: object) -> str:
    """Retourne le premier genre renseigné pour colorer les graphiques."""
    if pd.isna(valeur) or not str(valeur).strip():
        return "Non renseigné"
    return str(valeur).split(",")[0].strip()


def charger_avec_message(fonction, message: str):
    """Charge une source et affiche une erreur compréhensible si elle échoue."""
    try:
        return fonction()
    except Exception as erreur:
        st.error(message, icon=":material/cloud_off:")
        with st.expander("Afficher le détail technique"):
            st.exception(erreur)
        st.stop()


def reinitialiser_filtres() -> None:
    """Rétablit les filtres du catalogue à leur valeur initiale."""
    st.session_state.genres = []
    st.session_state.note_minimale = 0.0


if BANNIERE.exists():
    st.image(
        BANNIERE,
        width="stretch",
        alt="Tapis rouge devant un grand cinéma Art déco illuminé",
    )

st.title(":material/movie: CinéMatch")
st.caption("Le catalogue cinéma qui réunit exploration, recommandations et musique.")

with st.sidebar:
    st.header(":material/tune: Filtres")
    if st.button(
        "Actualiser les données",
        icon=":material/refresh:",
        width="stretch",
    ):
        obtenir_catalogue.clear()
        obtenir_recommandations.clear()
        obtenir_bandes_originales.clear()
        obtenir_oscars_films.clear()
        obtenir_oscars_series.clear()
        obtenir_profils_utilisateurs.clear()
        st.rerun()

catalogue = charger_avec_message(
    obtenir_catalogue,
    "Impossible de charger le catalogue. Vérifie la connexion Google Cloud puis réessaie.",
)

genres_disponibles = sorted(
    {
        genre.strip()
        for valeur in catalogue["genres"].dropna()
        for genre in valeur.split(",")
        if genre.strip() and genre.strip() != "Non renseigné"
    }
)

with st.sidebar:
    type_contenu = st.segmented_control(
        "Type de contenu",
        ["Films", "Séries"],
        default="Films",
        key="type_contenu",
    )
    genres_choisis = st.multiselect("Genres", genres_disponibles, key="genres")
    note_minimale = st.slider(
        "Note minimale",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
        key="note_minimale",
    )
    st.button(
        "Réinitialiser les filtres",
        icon=":material/filter_alt_off:",
        width="stretch",
        on_click=reinitialiser_filtres,
    )
    st.divider()
    st.caption(
        "Les filtres s'appliquent au catalogue, à la fiche détaillée "
        "et à la sélection des favoris."
    )

catalogue_filtre = filtrer_catalogue(
    catalogue,
    type_contenu or "Films",
    genres_choisis,
    note_minimale,
)

if catalogue_filtre.empty:
    st.info("Aucun contenu ne correspond à ces filtres.")
    st.stop()

note_moyenne = catalogue_filtre["rating_average"].mean()
resume_donnees = (
    f"{len(catalogue):,} contenus dans Gold · "
    "5 recommandations par œuvre · notes unifiées sur 10"
)
st.caption(resume_donnees.replace(",", " "))

page = st.pills(
    "Navigation",
    ["Catalogue", "Les Oscars", "Fiche", "Le Match", "Profils", "Bandes originales"],
    default="Catalogue",
    selection_mode="single",
    key="navigation_principale",
    label_visibility="collapsed",
)

if page == "Catalogue":
    st.header("Le catalogue à l'affiche")
    st.caption("Une vue d'ensemble des films et séries correspondant aux filtres.")

    with st.container(horizontal=True):
        st.metric("Contenus", f"{len(catalogue_filtre):,}".replace(",", " "), border=True)
        st.metric(
            "Note moyenne",
            f"{note_moyenne:.1f} / 10" if pd.notna(note_moyenne) else "Non disponible",
            border=True,
        )

    graphique, palmares = st.columns([1.2, 0.8])
    with graphique:
        with st.container(border=True):
            st.subheader(":material/trending_up: Les plus populaires")
            populaires = (
                catalogue_filtre.nlargest(12, "popularity")[["title", "popularity", "genres"]]
                .sort_values("popularity", ascending=False)
                .rename(columns={"title": "Titre", "popularity": "Popularité", "genres": "Genres"})
            )
            populaires["Genre principal"] = populaires["Genres"].map(genre_principal)
            populaires["Popularité"] = (
                populaires["Popularité"].round().astype(int)
            )
            graphique_popularite = (
                alt.Chart(populaires)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Popularité:Q",
                        title="Popularité",
                        axis=alt.Axis(format="d"),
                    ),
                    y=alt.Y(
                        "Titre:N",
                        title=None,
                        sort=alt.SortField(
                            field="Popularité",
                            order="descending",
                        ),
                    ),
                    color=alt.Color(
                        "Genre principal:N",
                        scale=alt.Scale(range=COULEURS_GENRES),
                        legend=alt.Legend(title="Genre principal"),
                    ),
                    tooltip=[
                        "Titre:N",
                        "Genre principal:N",
                        alt.Tooltip("Popularité:Q", format=".0f"),
                    ],
                )
            )
            st.altair_chart(
                graphique_popularite,
                alt="Les douze contenus les plus populaires du catalogue filtré",
            )

    with palmares:
        with st.container(border=True):
            st.subheader(":material/star: Le palmarès")
            mieux_notes = (
                catalogue_filtre[catalogue_filtre["rating_count"].fillna(0) >= 100]
                .nlargest(8, "rating_average")
                [["title", "content_type", "rating_average"]]
                .copy()
            )
            mieux_notes["content_type"] = mieux_notes["content_type"].map(
                {"movie": "Film", "tv": "Série"}
            )
            st.dataframe(
                mieux_notes.rename(
                    columns={
                        "title": "Titre",
                        "content_type": "Type",
                        "rating_average": "Note",
                    }
                ),
                hide_index=True,
                alt="Les contenus les mieux notés avec au moins cent votes",
                column_config={"Note": st.column_config.NumberColumn(format="%.1f")},
            )

    with st.container(border=True):
        st.subheader(":material/view_list: Tous les contenus")
        tableau = catalogue_filtre[
            ["title", "content_type", "start_year", "genres", "rating_average", "popularity"]
        ].rename(
            columns={
                "title": "Titre",
                "content_type": "Type",
                "start_year": "Année",
                "genres": "Genres",
                "rating_average": "Note",
                "popularity": "Popularité",
            }
        )
        tableau["Type"] = tableau["Type"].map({"movie": "Film", "tv": "Série"})
        st.dataframe(
            tableau,
            hide_index=True,
            alt="Catalogue des films et séries correspondant aux filtres",
            column_config={
                "Note": st.column_config.NumberColumn(format="%.1f"),
                "Popularité": st.column_config.NumberColumn(format="%.1f"),
            },
        )

if page == "Les Oscars":
    oscars_films = charger_avec_message(obtenir_oscars_films, "Le palmarès des films est indisponible.")
    oscars_series = charger_avec_message(obtenir_oscars_series, "Le palmarès des séries est indisponible.")
    st.header(":material/trophy: Les Oscars de CinéMatch")
    st.caption(
        "Un palmarès calculé à partir du catalogue Gold. Les prix liés à la note "
        "exigent au moins 100 votes ; le ROI exige un budget d'au moins 1 M$."
    )
    categorie_oscars = st.segmented_control(
        "Choisir un palmarès",
        ["Films", "Séries"],
        default="Films",
        key="categorie_oscars",
    )
    aujourd_hui = pd.Timestamp.today().normalize()

    if categorie_oscars == "Films":
        films = oscars_films.copy()
        films["release_date"] = pd.to_datetime(
            films["release_date"], errors="coerce"
        )
        films_notes = films[
            (films["rating_count"].fillna(0) >= 100)
            & films["rating_average"].notna()
        ]
        films_dates = films[
            films["release_date"].notna()
            & (films["release_date"] <= aujourd_hui)
        ]
        films_durees = films[films["runtime"].fillna(0) >= 40]
        films_finance = films[
            (films["budget"].fillna(0) > 0)
            & (films["revenue"].fillna(0) > 0)
        ]
        films_roi = films_finance[films_finance["budget"] >= 1_000_000]

        meilleur_note = gagnant(films_notes, "rating_average")
        populaire = gagnant(films, "popularity")
        meilleur_roi = gagnant(films_roi, "roi")
        meilleur_benefice = gagnant(films_finance, "profit")
        meilleure_recette = gagnant(films_finance, "revenue")
        plus_gros_budget = gagnant(films_finance, "budget")
        plus_long = gagnant(films_durees, "runtime")
        plus_court = gagnant(films_durees, "runtime", maximum=False)
        plus_ancien = gagnant(films_dates, "release_date", maximum=False)
        plus_recent = gagnant(films_dates, "release_date")

        prix_films = [
            (
                "Meilleur film",
                meilleur_note,
                f"{meilleur_note['rating_average']:.1f} / 10"
                if meilleur_note is not None else "",
            ),
            (
                "Prix du public",
                populaire,
                f"Popularité {populaire['popularity']:.0f}"
                if populaire is not None else "",
            ),
            (
                "Meilleur ROI",
                meilleur_roi,
                f"{meilleur_roi['roi'] * 100:.0f} %"
                if meilleur_roi is not None else "",
            ),
            (
                "Meilleur bénéfice",
                meilleur_benefice,
                montant(meilleur_benefice["profit"])
                if meilleur_benefice is not None else "",
            ),
            (
                "Meilleure recette",
                meilleure_recette,
                montant(meilleure_recette["revenue"])
                if meilleure_recette is not None else "",
            ),
            (
                "Plus gros budget",
                plus_gros_budget,
                montant(plus_gros_budget["budget"])
                if plus_gros_budget is not None else "",
            ),
            (
                "Film le plus long",
                plus_long,
                f"{int(plus_long['runtime'])} minutes"
                if plus_long is not None else "",
            ),
            (
                "Film le plus court",
                plus_court,
                f"{int(plus_court['runtime'])} minutes"
                if plus_court is not None else "",
            ),
            (
                "Doyen du catalogue",
                plus_ancien,
                str(plus_ancien["release_date"].year)
                if plus_ancien is not None else "",
            ),
            (
                "Film le plus récent",
                plus_recent,
                str(plus_recent["release_date"].year)
                if plus_recent is not None else "",
            ),
        ]
        afficher_prix(prix_films)
        gagnants_genres = meilleurs_par_genre(films)

    else:
        series = oscars_series.copy()
        series["first_air_date"] = pd.to_datetime(
            series["first_air_date"], errors="coerce"
        )
        series_notes = series[
            (series["rating_count"].fillna(0) >= 100)
            & series["rating_average"].notna()
        ]
        series_dates = series[
            series["first_air_date"].notna()
            & (series["first_air_date"] <= aujourd_hui)
        ]
        series_saisons = series[series["number_of_seasons"].fillna(0) > 0]
        series_episodes = series[series["number_of_episodes"].fillna(0) > 0]
        series_durees = series[series["duration_days"].fillna(0) >= 0]
        en_production = series_notes[series_notes["in_production"].fillna(False)]

        meilleure_note = gagnant(series_notes, "rating_average")
        populaire = gagnant(series, "popularity")
        saisons = gagnant(series_saisons, "number_of_seasons")
        episodes = gagnant(series_episodes, "number_of_episodes")
        longevite = gagnant(series_durees, "duration_days")
        plus_ancienne = gagnant(series_dates, "first_air_date", maximum=False)
        plus_recente = gagnant(series_dates, "first_air_date")
        active = gagnant(en_production, "rating_average")

        prix_series = [
            (
                "Meilleure série",
                meilleure_note,
                f"{meilleure_note['rating_average']:.1f} / 10"
                if meilleure_note is not None else "",
            ),
            (
                "Prix du public",
                populaire,
                f"Popularité {populaire['popularity']:.0f}"
                if populaire is not None else "",
            ),
            (
                "Plus de saisons",
                saisons,
                f"{int(saisons['number_of_seasons'])} saisons"
                if saisons is not None else "",
            ),
            (
                "Plus d'épisodes",
                episodes,
                f"{int(episodes['number_of_episodes'])} épisodes"
                if episodes is not None else "",
            ),
            (
                "Plus grande longévité",
                longevite,
                f"{longevite['duration_days'] / 365.25:.1f} ans"
                if longevite is not None else "",
            ),
            (
                "Doyenne du catalogue",
                plus_ancienne,
                str(plus_ancienne["first_air_date"].year)
                if plus_ancienne is not None else "",
            ),
            (
                "Série la plus récente",
                plus_recente,
                str(plus_recente["first_air_date"].year)
                if plus_recente is not None else "",
            ),
            (
                "Meilleure série en production",
                active,
                f"{active['rating_average']:.1f} / 10"
                if active is not None else "",
            ),
        ]
        afficher_prix(prix_series)
        gagnants_genres = meilleurs_par_genre(series)

    st.subheader(":material/stars: Les meilleurs par genre")
    st.caption(
        "Une œuvre concourt dans chacun de ses genres. En cas d'égalité, "
        "le nombre d'évaluations départage les candidats."
    )
    tableau_genres = gagnants_genres[
        ["genre", "title", "rating_average", "rating_count"]
    ].rename(
        columns={
            "genre": "Genre",
            "title": "Lauréat",
            "rating_average": "Note",
            "rating_count": "Évaluations",
        }
    )
    st.dataframe(
        tableau_genres,
        hide_index=True,
        alt="Meilleure œuvre de chaque genre avec au moins cent évaluations",
        column_config={
            "Note": st.column_config.NumberColumn(format="%.1f"),
            "Évaluations": st.column_config.NumberColumn(format="%d"),
        },
    )

if page == "Fiche":
    recommandations = charger_avec_message(obtenir_recommandations, "Les recommandations sont indisponibles.")
    bandes_originales = charger_avec_message(obtenir_bandes_originales, "Les bandes originales sont indisponibles.")
    st.header("Sous les projecteurs")
    st.caption(
        "Choisis une œuvre pour afficher sa fiche, sa musique "
        "et les cinq contenus qui lui ressemblent le plus."
    )
    choix = st.selectbox(
        "Rechercher un titre",
        catalogue_filtre["content_key"].tolist(),
        format_func=lambda cle: nom_contenu(cle, catalogue_filtre),
        key="contenu_selectionne",
    )
    contenu = catalogue_filtre[catalogue_filtre["content_key"] == choix].iloc[0]

    with st.container(border=True):
        image, details = st.columns([0.28, 0.72])
        with image:
            if pd.notna(contenu["poster_url"]):
                st.image(
                    contenu["poster_url"],
                    alt=f"Affiche de {contenu['title']}",
                )
            else:
                st.info("Affiche non disponible.")

        with details:
            st.subheader(contenu["title"])
            type_lisible = "Film" if contenu["content_type"] == "movie" else "Série"
            annee = (
                int(contenu["start_year"])
                if pd.notna(contenu["start_year"])
                else "année inconnue"
            )
            st.caption(f"{type_lisible} · {annee} · {contenu['genres']}")
            st.markdown(contenu["overview"] or "Résumé non disponible.")

            with st.container(horizontal=True):
                note = contenu["rating_average"]
                st.metric(
                    "Note moyenne",
                    f"{note:.1f} / 10" if pd.notna(note) else "Non disponible",
                    border=True,
                )
                st.metric(
                    "Popularité",
                    f"{contenu['popularity']:.1f}"
                    if pd.notna(contenu["popularity"])
                    else "Non disponible",
                    border=True,
                )
                st.metric(
                    "Évaluations",
                    f"{int(contenu['rating_count']):,}".replace(",", " ")
                    if pd.notna(contenu["rating_count"])
                    else "Non disponible",
                    border=True,
                )

            bande_originale = bandes_originales[
                bandes_originales["content_key"] == choix
            ]
            if (
                not bande_originale.empty
                and pd.notna(bande_originale.iloc[0]["soundtrack_title"])
            ):
                bo = bande_originale.iloc[0]
                st.success(
                    f"Bande originale : {bo['soundtrack_title']}",
                    icon=":material/music_note:",
                )
                precision = (
                    f" · fiabilité {bo['match_score']:.0f}/100"
                    if pd.notna(bo.get("match_score"))
                    else ""
                )
                st.caption(f"Compositeur : {bo['composer_name']}{precision}")

    with st.container(border=True):
        st.subheader(":material/recommend: Les cinq contenus similaires")
        resultats = (
            recommandations[
                (recommandations["source_content_key"] == choix)
                & (
                    recommandations["recommended_content_type"]
                    == contenu["content_type"]
                )
            ]
            .sort_values("rank")
            .head(5)
            .copy()
        )
        if resultats.empty:
            st.info("Aucune recommandation disponible pour ce contenu.")
        else:
            resultats["recommended_content_type"] = resultats[
                "recommended_content_type"
            ].map({"movie": "Film", "tv": "Série"})
            resultats["similarity_score"] *= 100
            st.dataframe(
                resultats[
                    [
                        "rank",
                        "recommended_title",
                        "recommended_content_type",
                        "start_year",
                        "rating_average",
                        "similarity_score",
                    ]
                ].rename(
                    columns={
                        "rank": "Rang",
                        "recommended_title": "Titre recommandé",
                        "recommended_content_type": "Type",
                        "start_year": "Année",
                        "rating_average": "Note moyenne",
                        "similarity_score": "Similarité",
                    }
                ),
                hide_index=True,
                alt="Les cinq contenus les plus proches du titre sélectionné",
                column_config={
                    "Note moyenne": st.column_config.NumberColumn(format="%.1f"),
                    "Similarité": st.column_config.ProgressColumn(
                        format="%.1f %%",
                        min_value=0,
                        max_value=100,
                    ),
                },
            )

if page == "Le Match":
    recommandations = charger_avec_message(obtenir_recommandations, "Le Match est momentanément indisponible.")
    st.header("Le Match")
    st.caption(
        "Compose ton programme idéal : choisis au moins deux œuvres "
        "et CinéMatch croise leurs recommandations."
    )
    with st.container(border=True):
        favoris = st.multiselect(
            "Les œuvres que j'aime",
            catalogue_filtre["content_key"].tolist(),
            format_func=lambda cle: nom_contenu(cle, catalogue_filtre),
            key="favoris",
            max_selections=10,
        )
        if len(favoris) < 2:
            st.info(
                "Sélectionne au moins deux favoris pour créer ton profil.",
                icon=":material/favorite:",
            )
        else:
            profil = recommander_selon_favoris(
                favoris,
                recommandations,
                catalogue_filtre,
                nombre=5,
            )
            if profil.empty:
                st.info("Aucun résultat commun n'a été trouvé. Essaie d'autres favoris.")
                st.stop()
            profil["content_type"] = profil["content_type"].map(
                {"movie": "Film", "tv": "Série"}
            )
            st.success(
                "Ton palmarès personnalisé est prêt.",
                icon=":material/celebration:",
            )
            st.dataframe(
                profil[
                    [
                        "title",
                        "content_type",
                        "start_year",
                        "rating_average",
                        "score_personnel",
                    ]
                ].rename(
                    columns={
                        "title": "Titre",
                        "content_type": "Type",
                        "start_year": "Année",
                        "rating_average": "Note moyenne",
                        "score_personnel": "Score du Match",
                    }
                ),
                hide_index=True,
                alt="Les cinq recommandations calculées à partir des favoris",
                column_config={
                    "Note moyenne": st.column_config.NumberColumn(format="%.1f"),
                    "Score du Match": st.column_config.ProgressColumn(
                        format="%.2f",
                        min_value=0.0,
                        max_value=max(float(profil["score_personnel"].max()), 1.0),
                    ),
                },
            )

if page == "Profils":
    profils_utilisateurs, preferences_segments = charger_avec_message(
        obtenir_profils_utilisateurs,
        "Les profils de spectateurs sont momentanément indisponibles.",
    )
    st.header(":material/groups: Les profils de spectateurs")
    st.caption(
        "Les 610 utilisateurs MovieLens sont regroupés selon leurs écarts de "
        "notation par genre. Les identifiants restent entièrement anonymes."
    )
    if profils_utilisateurs.empty:
        st.info("Aucun profil utilisateur n'est disponible.")
        st.stop()
    silhouette = profils_utilisateurs["silhouette"].iloc[0]
    with st.container(horizontal=True):
        st.metric(
            "Utilisateurs",
            f"{int(profils_utilisateurs['nombre_utilisateurs'].sum()):,}".replace(",", " "),
            border=True,
        )
        st.metric("Profils", len(profils_utilisateurs), border=True)
        st.metric("Qualité de séparation", f"{silhouette:.3f}", border=True)
    st.info(
        "Le score de silhouette est faible : ces profils décrivent des tendances "
        "de goûts, pas des catégories de spectateurs parfaitement séparées.",
        icon=":material/info:",
    )

    tailles = profils_utilisateurs[
        ["nom_segment", "nombre_utilisateurs"]
    ].rename(
        columns={
            "nom_segment": "Profil",
            "nombre_utilisateurs": "Utilisateurs",
        }
    )
    graphique_profils = (
        alt.Chart(tailles)
        .mark_bar()
        .encode(
            x=alt.X("Utilisateurs:Q", title="Utilisateurs"),
            y=alt.Y("Profil:N", title=None, sort="-x"),
            tooltip=["Profil:N", "Utilisateurs:Q"],
        )
    )
    st.altair_chart(
        graphique_profils,
        alt="Nombre d'utilisateurs dans chacun des trois profils",
    )

    choix_segment = st.selectbox(
        "Explorer un profil",
        profils_utilisateurs["segment_id"].tolist(),
        format_func=lambda identifiant: profils_utilisateurs.loc[
            profils_utilisateurs["segment_id"] == identifiant,
            "nom_segment",
        ].iloc[0],
        key="profil_utilisateur",
    )
    profil = profils_utilisateurs[
        profils_utilisateurs["segment_id"] == choix_segment
    ].iloc[0]
    st.subheader(profil["nom_segment"])
    st.caption(
        f"Genres caractéristiques : {profil['genre_1']}, "
        f"{profil['genre_2']} et {profil['genre_3']}"
    )
    favoris_segment = preferences_segments[
        preferences_segments["segment_id"] == choix_segment
    ][
        [
            "rang",
            "title",
            "note_moyenne_segment",
            "nombre_notes_segment",
            "score_pondere",
        ]
    ].rename(
        columns={
            "rang": "Rang",
            "title": "Film",
            "note_moyenne_segment": "Note moyenne",
            "nombre_notes_segment": "Nombre de notes",
            "score_pondere": "Score pondéré",
        }
    )
    st.dataframe(
        favoris_segment,
        hide_index=True,
        alt="Les cinq films caractéristiques du profil sélectionné",
        column_config={
            "Note moyenne": st.column_config.NumberColumn(format="%.2f"),
            "Score pondéré": st.column_config.NumberColumn(format="%.2f"),
        },
    )

if page == "Bandes originales":
    bandes_originales = charger_avec_message(obtenir_bandes_originales, "Les bandes originales sont indisponibles.")
    bo_valides = bandes_originales[
        bandes_originales["soundtrack_title"].notna()
        & bandes_originales["content_key"].isin(catalogue_filtre["content_key"])
    ].copy()
    if bo_valides.empty:
        st.info(
            "Aucune bande originale ne correspond aux filtres actuels. "
            "Essaie un autre genre ou une note minimale plus basse.",
            icon=":material/music_off:",
        )
        st.stop()
    st.header("La cérémonie en musique")
    st.caption(
        "Explore les bandes originales rapprochées avec MusicBrainz "
        "et le score de confiance calculé par CineMatch."
    )
    with st.container(horizontal=True):
        st.metric(
            "BO identifiées",
            f"{len(bo_valides):,}".replace(",", " "),
            border=True,
        )
        st.metric(
            "Compositeurs",
            f"{bo_valides['composer_name'].nunique():,}".replace(",", " "),
            border=True,
        )
        score_moyen = bo_valides["match_score"].mean()
        st.metric(
            "Fiabilité moyenne",
            f"{score_moyen:.0f} / 100" if pd.notna(score_moyen) else "Non disponible",
            border=True,
        )

    bo_affichees = bo_valides.merge(
        catalogue_filtre[["content_key", "content_type", "start_year"]],
        on="content_key",
        how="left",
    )
    bo_affichees["content_type"] = bo_affichees["content_type"].map(
        {"movie": "Film", "tv": "Série"}
    )

    with st.container(border=True):
        st.subheader(":material/album: Retrouver les œuvres d'une BO")
        bo_choisie = st.selectbox(
            "Choisir une bande originale",
            sorted(bo_affichees["soundtrack_title"].dropna().unique()),
            key="bo_selectionnee",
        )
        oeuvres_associees = bo_affichees[
            bo_affichees["soundtrack_title"] == bo_choisie
        ].copy()

        premiere_bo = oeuvres_associees.iloc[0]
        st.caption(
            f"Compositeur : {premiere_bo['composer_name']} · "
            f"{len(oeuvres_associees)} œuvre(s) associée(s)"
        )
        if pd.notna(premiere_bo.get("musicbrainz_id")):
            st.link_button(
                "Ouvrir cette BO sur MusicBrainz",
                (
                    "https://musicbrainz.org/release-group/"
                    f"{premiere_bo['musicbrainz_id']}"
                ),
                icon=":material/open_in_new:",
            )

        st.dataframe(
            oeuvres_associees[
                ["title", "content_type", "start_year"]
            ].rename(
                columns={
                    "title": "Œuvre associée",
                    "content_type": "Type",
                    "start_year": "Année",
                }
            ),
            hide_index=True,
            alt="Œuvres associées à la bande originale sélectionnée",
        )

    with st.container(border=True):
        st.subheader(":material/library_music: Toutes les bandes originales")
        st.dataframe(
            bo_affichees[
                [
                    "title",
                    "content_type",
                    "start_year",
                    "composer_name",
                    "soundtrack_title",
                ]
            ].rename(
                columns={
                    "title": "Œuvre",
                    "content_type": "Type",
                    "start_year": "Année",
                    "composer_name": "Compositeur",
                    "soundtrack_title": "Bande originale",
                }
            ),
            hide_index=True,
            alt="Bandes originales MusicBrainz associées au catalogue",
        )

