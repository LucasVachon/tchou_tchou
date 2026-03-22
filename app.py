import streamlit as st
import pandas as pd
import pydeck as pdk
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TCHOU TCHOU",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.spinner("⏳ Chargement des données..."):
    try:
        festivals_df = pd.read_csv(
            "./data/festivals-global-festivals-pl-avec-dates-V2.csv", sep=";"
        )
        gares_df = pd.read_csv(
            "./data/gares-de-voyageurs.csv", sep=";"
        )
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        st.stop()


st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
    }
    .highlight {
        background-color: #FFE8E8;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)

if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "festival_select" not in st.session_state:
    st.session_state["festival_select"] = None

with st.container():
    st.markdown(
        "<h1 class='main-title'>Découverte de Festivals avec TCHOU TCHOU</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            "<p class='subtitle'>Explorez les festivals à proximité et planifiez "
            "votre itinéraire optimal en train</p>"
        ),
        unsafe_allow_html=True,
    )

options = ["recherche", "statistiques"]
selection = st.radio("Navigation", options, index=0, label_visibility="collapsed")

if selection == "statistiques":
    st.subheader("Statistiques")
    st.markdown(
        """
La région la mieux desservie est l'**Île-de-France** avec **653 festivals** dont **650 bien desservis (99,5 %)**.
La distance moyenne d'une gare à un festival y est de **1,88 km**.

**Régions les moins bien desservies :**

1. **Bretagne**
   - Festivals : 590
   - Mal desservis : 32 (5,4 %)
   - Distance moyenne : 9,56 km

2. **Auvergne-Rhône-Alpes**
   - Festivals : 947
   - Mal desservis : 50 (5,3 %)
   - Distance moyenne : 8,02 km

3. **Occitanie**
   - Festivals : 900
   - Mal desservis : 45 (5,0 %)
   - Distance moyenne : 9,25 km
"""
    )

    st.markdown("### Nombre de festivals par département")
    st.image("./figure1.png", width="stretch")

    st.markdown("### Carte interactive de la couverture ferroviaire")
    html_paths = [
        "./output_map_chevauchement_metropole.html",
        "./output_map_chevauchement.html",
    ]
    stats_html = None
    for html_path in html_paths:
        try:
            with open(html_path, "r", encoding="utf-8") as html_file:
                stats_html = html_file.read()
            break
        except FileNotFoundError:
            continue

    if stats_html:
        components.html(stats_html, height=760, scrolling=True)
    else:
        st.info("Carte interactive non trouvée dans le dépôt (fichier HTML manquant).")
else:
    event_date = pd.Timestamp(st.date_input("Quand voulez‑vous partir ?"))

    gare_options = gares_df["Nom"].dropna().unique().tolist()
    gare_de_depart = st.multiselect(
        "Quelles sont les gares les plus proches de chez vous ?",
        gare_options,
    )

    if st.button("rechercher les festivals"):
        st.session_state["searched"] = True

    if st.session_state["searched"]:

        box1, box2 = st.columns([2, 1])

        df_work = festivals_df.copy()

        df_work["Date de début"] = pd.to_datetime(
            df_work["Date de début"]).dt.strftime(
            '%Y-%m-%d').str.replace('2019', '2026')
        df_work["Date de début"] = pd.to_datetime(df_work["Date de début"])
        df_work["Date de fin"] = pd.to_datetime(
            df_work["Date de fin"]).dt.strftime(
            '%Y-%m-%d').str.replace('2019', '2026')
        df_work["Date de fin"] = pd.to_datetime(df_work["Date de fin"])

        df_work[["lat", "lon"]] = df_work["Géocodage xy"].str.split(
            ",", expand=True).astype(float)

        festivals_filtres = df_work[
            (df_work["Date de début"] <= event_date) &
            (event_date <= df_work["Date de fin"])
        ]

        if festivals_filtres.empty:
            st.warning("Aucun festival à cette date...")
        else:

            with box2:
                liste_type_festival = festivals_filtres[
                    "Discipline dominante"
                ].dropna().unique().tolist()
                st.title("Filtres")
                filtre_type = st.multiselect(
                    "Type de festival",
                    liste_type_festival,
                    default=liste_type_festival,
                )
                if st.session_state["festival_select"]:
                    festival_row = df_work[df_work["Nom du festival"]
                                           == st.session_state["festival_select"]]
                    st.title("Détails")
                    with st.container(border=True):
                        st.subheader(festival_row["Nom du festival"].values[0])
                        st.text(
                            "region : "
                            + festival_row[
                                "Région principale de déroulement"
                            ].values[0]
                        )
                        date_debut = pd.to_datetime(
                            festival_row["Date de début"].values[0]
                        ).strftime("%Y-%m-%d")
                        date_fin = pd.to_datetime(
                            festival_row["Date de fin"].values[0]
                        ).strftime("%Y-%m-%d")
                        st.text(f"dates : du {date_debut} au {date_fin}")
                        st.text(
                            "type de festival : "
                            + festival_row["Discipline dominante"].values[0]
                        )
                        st.button("calculer l'itineraire en train")

            # Apply the type filter to the results
            if filtre_type:
                festivals_filtres = festivals_filtres[
                    festivals_filtres["Discipline dominante"].isin(filtre_type)
                ]

            with box1:
                st.title(str(len(festivals_filtres)) + " résultats")
                tab1, tab2 = st.tabs(["Liste", "Carte"])
                with tab1:
                    display_cols = [
                        "Nom du festival",
                        "Discipline dominante",
                        "Date de début",
                        "Date de fin",
                    ]
                    with st.container(height=500, border=False):
                        for i, row in festivals_filtres.iterrows():

                            with st.container(border=True):
                                col1, col2, col3, col4 = st.columns(
                                    [1, 3, 2, 2]
                                )

                                with col1:
                                    if st.button("select", key=f"select_{i}"):
                                        st.session_state[
                                            "festival_select"
                                        ] = row["Nom du festival"]

                                with col2:
                                    st.write(row["Nom du festival"])

                                with col3:
                                    st.write(row["Discipline dominante"])

                                with col4:
                                    s = row["Date de début"].strftime(
                                        "%Y-%m-%d"
                                    )
                                    e = row["Date de fin"].strftime(
                                        "%Y-%m-%d"
                                    )
                                    st.write(f"{s} - {e}")

                with tab2:
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=festivals_filtres,
                        get_position=["lon", "lat"],
                        get_fill_color=[255, 107, 107],
                        get_radius=10000,
                        pickable=True,
                    )

                    view_state = pdk.ViewState(
                        latitude=festivals_filtres["lat"].mean(),
                        longitude=festivals_filtres["lon"].mean(),
                        zoom=5,
                    )

                    deck = pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        tooltip={"text": "{Nom du festival}",
                                 "region": "{Région principale de déroulement}"}
                    )

                    selected_data = st.pydeck_chart(deck)
