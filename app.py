import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime
from dotenv import load_dotenv
import os
import math
import streamlit.components.v1 as components

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="TCHOU TCHOU - Festival & Train",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement des variables d'environnement
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")
BASE_URL = "https://api.sncf.com/v1/coverage/sncf"

# Chemins des fichiers
CSV_FESTIVALS = "festivals-global-festivals-pl-avec-dates-V2.csv"
CSV_GARES = "gares-de-voyageurs.csv"

# ==========================================
# 0. STYLE CSS
# ==========================================
st.markdown("""
<style>
    .main-title { text-align: center; color: #FF6B6B; margin-bottom: 10px; }
    .subtitle { text-align: center; color: #666; font-size: 18px; }
    .highlight { background-color: #FFE8E8; padding: 10px; border-radius: 5px; border-left: 4px solid #FF6B6B; }
    
    .trajet-card {
        background-color: #ffffff; border-radius: 8px; padding: 10px 15px; 
        margin-bottom: 8px; border-left: 5px solid #ccc; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s;
    }
    .trajet-card:hover { transform: translateY(-1px); box-shadow: 0 3px 6px rgba(0,0,0,0.15); }
    .tgv { border-left-color: #9b59b6; background-color: #fcf4ff; }
    .ter { border-left-color: #3498db; background-color: #f0f8ff; }
    .intercites { border-left-color: #27ae60; background-color: #effcf5; }
    .autocar { border-left-color: #FF9F43; background-color: #FFF6EA; }
    .header-train { display: flex; align-items: center; margin-bottom: 6px; }
    .badge { padding: 3px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.75em; margin-right: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-tgv { background-color: #9b59b6; }
    .badge-ter { background-color: #3498db; }
    .badge-intercites { background-color: #27ae60; }
    .badge-autocar { background-color: #FF9F43; }
    .badge-other { background-color: #95a5a6; }
    .train-num { color: #7f8c8d; font-weight: 500; font-size: 0.8em; }
    .time-grid { display: grid; grid-template-columns: 1fr 40px 1fr; align-items: center; }
    .time-grid > div:last-child { text-align: right; }
    .arrow-col { text-align: center; color: #bdc3c7; font-size: 1.2em; margin-top: -5px; }
    .hour { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 1.2em; font-weight: 700; color: #2c3e50; line-height: 1; }
    .station-name { font-size: 0.85em; color: #576574; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .correspondance { text-align: center; color: #95a5a6; font-size: 0.8em; margin: 4px 0; font-style: italic; display: flex; align-items: center; justify-content: center; }
    .correspondance::before, .correspondance::after { content: ""; flex: 1; border-bottom: 1px dashed #e0e0e0; margin: 0 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. FONCTIONS BACKEND
# ==========================================


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


@st.cache_data
def charger_donnees():
    try:
        df_festivals = pd.read_csv(CSV_FESTIVALS, sep=";")

        df_gares = pd.read_csv(CSV_GARES, sep=';', dtype={'Code(s) UIC': str})
        df_gares = df_gares.dropna(
            subset=['Nom', 'Position géographique']).drop_duplicates(subset=['Nom'])
        df_gares[['lat', 'lon']] = df_gares['Position géographique'].str.split(
            ',', expand=True).astype(float)
        df_gares = df_gares.sort_values('Nom')

        return df_festivals, df_gares
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        st.stop()


def trouver_gare_plus_proche(lat_fest, lon_fest, df_gares):
    distances = df_gares.apply(lambda row: haversine(
        lat_fest, lon_fest, row['lat'], row['lon']), axis=1)
    index_proche = distances.idxmin()
    return df_gares.loc[index_proche]


def formater_id_sncf(code_uic):
    code = str(code_uic).split(';')[0].strip()
    return f"stop_area:SNCF:{code}"


def format_heure_affichage(str_date):
    dt = datetime.strptime(str_date, "%Y%m%dT%H%M%S")
    return dt.strftime("%Hh%M")


def nettoyer_nom_gare(nom):
    if "(" in nom:
        nom = nom.split("(")[0].strip()
    return nom


def detecter_type_train(raw_mode):
    mode_lower = raw_mode.lower()
    if "grande vitesse" in mode_lower or "tgv" in mode_lower or "ouigo" in mode_lower:
        return "TGV", "tgv"
    elif "ter" in mode_lower:
        return "TER", "ter"
    elif "intercités" in mode_lower:
        return "Intercités", "intercites"
    elif "autocar" in mode_lower or "bus" in mode_lower:
        return "Autocar", "autocar"
    else:
        return raw_mode.capitalize(), "other"


def get_journeys_detailed(id_dep, id_arr, date_obj):
    date_str_api = date_obj.strftime("%Y%m%dT000000")
    date_filter = date_obj.strftime("%Y%m%d")
    url = f"{BASE_URL}/journeys"
    params = {'from': id_dep, 'to': id_arr,
              'datetime': date_str_api, 'min_nb_journeys': 20}

    try:
        response = requests.get(url, params=params, auth=(API_KEY, ''))
        response.raise_for_status()
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None

    data = response.json()
    if 'journeys' not in data:
        return []
    return [j for j in data['journeys'] if j['departure_date_time'][:8] == date_filter]

# ==========================================
# 2. INITIALISATION DU SESSION STATE
# ==========================================


if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "festival_select" not in st.session_state:
    st.session_state["festival_select"] = None
if "show_itinerary" not in st.session_state:
    st.session_state["show_itinerary"] = False
if "gare_arrivee_auto" not in st.session_state:
    st.session_state["gare_arrivee_auto"] = None

with st.spinner("⏳ Chargement des données..."):
    festivals_df, gares_df = charger_donnees()

# ==========================================
# 3. INTERFACE PRINCIPALE
# ==========================================

with st.container():
    st.markdown("<h1 class='main-title'>Découverte de Festivals avec TCHOU TCHOU</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Explorez les festivals à proximité et planifiez votre itinéraire optimal en train</p>", unsafe_allow_html=True)

options = ["recherche", "statistiques"]
selection = st.radio("", options, index=0)

# ==========================================
# ONGLET STATISTIQUES
# ==========================================
if selection == "statistiques":
    st.session_state["show_itinerary"] = False  # Désactive le trajet

    st.subheader(
        "Visualisez l'offre culturelle et la couverture ferroviaire française !")

    st.markdown("### Nombre de festivals par département")
    try:
        st.image("./figure1.png", use_container_width=True)
    except FileNotFoundError:
        st.warning("L'image ./figure1.png n'a pas été trouvée.")

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

# ==========================================
# ONGLET RECHERCHE
# ==========================================
else:
    event_date_debut = pd.Timestamp(st.date_input(
        "À partir de quand voulez-vous partir ?", format="DD/MM/YYYY"))
    event_date_fin = pd.Timestamp(st.date_input(
        "Jusqu'à quand voulez-vous partir ?", format="DD/MM/YYYY"))

    if st.button("rechercher les festivals"):
        st.session_state["searched"] = True
        st.session_state["show_itinerary"] = False

    if st.session_state["searched"]:
        box1, box2 = st.columns([2, 1])
        df_work = festivals_df.copy()

        df_work["Date de début"] = pd.to_datetime(
            df_work["Date de début"]).dt.strftime('%Y-%m-%d').str.replace('2019', '2026')
        df_work["Date de début"] = pd.to_datetime(df_work["Date de début"])
        df_work["Date de fin"] = pd.to_datetime(df_work["Date de fin"]).dt.strftime(
            '%Y-%m-%d').str.replace('2019', '2026')
        df_work["Date de fin"] = pd.to_datetime(df_work["Date de fin"])
        df_work[["lat", "lon"]] = df_work["Géocodage xy"].str.split(
            ",", expand=True).astype(float)

        festivals_filtres = df_work[
            (df_work["Date de début"] <= event_date_fin) &
            (event_date_debut <= df_work["Date de fin"])
        ]

        if festivals_filtres.empty:
            st.warning("Aucun festival à cette date...")
        else:
            with box2:
                liste_type_festival = festivals_filtres["Discipline dominante"].dropna(
                ).unique().tolist()
                st.title("Filtres")
                filtre_type = st.multiselect(
                    "Type de festival", liste_type_festival, default=liste_type_festival)

                if st.session_state["festival_select"]:
                    festival_row = df_work[df_work["Nom du festival"]
                                           == st.session_state["festival_select"]].iloc[0]
                    st.title("Détails")
                    with st.container(border=True):
                        st.subheader(festival_row["Nom du festival"])
                        st.text(
                            "Région : " + festival_row["Région principale de déroulement"])

                        # --- MODIFICATION ICI : Format JJ/MM/AAAA ---
                        date_debut = pd.to_datetime(
                            festival_row["Date de début"]).strftime("%d/%m/%Y")
                        date_fin = pd.to_datetime(
                            festival_row["Date de fin"]).strftime("%d/%m/%Y")

                        st.text(f"Dates : du {date_debut} au {date_fin}")
                        st.text(
                            "Type : " + festival_row["Discipline dominante"])

                        if festival_row["Source date"] != "period-fallback" and festival_row["Source date"] != "seed:festivals-global-festivals-pl-avec-dates-10-premiers.csv":
                            url = festival_row["Source date"]
                            st.markdown(
                                f"Lien : [{festival_row['Source date']}]({url})")

                        st.markdown("---")

                        grandes_gares_only = st.checkbox(
                            "Grandes gares uniquement (TGV/Intercités)", value=False)

                        fest_lat = festival_row["lat"]
                        fest_lon = festival_row["lon"]

                        gares_cibles = gares_df
                        if grandes_gares_only:
                            gares_cibles = gares_df[gares_df["Segment(s) DRG"].isin([
                                "A", "A;A"])]
                            if gares_cibles.empty:
                                gares_cibles = gares_df

                        gare_proche = trouver_gare_plus_proche(
                            fest_lat, fest_lon, gares_cibles)

                        st.markdown(
                            f"**🚆 Gare la plus proche :** {gare_proche['Nom']}")

                        if st.button("Calculer l'itinéraire en train", type="primary"):
                            st.session_state["show_itinerary"] = True
                            st.session_state["gare_arrivee_auto"] = gare_proche['Nom']
                            st.rerun()

            if filtre_type:
                festivals_filtres = festivals_filtres[festivals_filtres["Discipline dominante"].isin(
                    filtre_type)]

            with box1:
                st.title(str(len(festivals_filtres)) + " résultats")

                liste_nom_festival = festivals_filtres["Nom du festival"].dropna(
                ).unique().tolist()
                search_festival = st.selectbox(
                    "🔍 Rechercher un festival par nom",
                    liste_nom_festival,
                    index=None
                )

                if search_festival:
                    festivals_filtres = festivals_filtres[
                        festivals_filtres["Nom du festival"].str.contains(
                            search_festival, case=False, na=False
                        )
                    ]

                tab1, tab2 = st.tabs(["Liste", "Carte"])

                with tab1:
                    with st.container(height=500, border=False):
                        for i, row in festivals_filtres.iterrows():
                            with st.container(border=True):
                                col1, col2, col3, col4 = st.columns(
                                    [0.8, 3, 2, 2])
                                with col1:
                                    if st.button("🔎 Détails", key=f"select_{i}", use_container_width=True):
                                        st.session_state["festival_select"] = row["Nom du festival"]
                                        st.session_state["show_itinerary"] = False
                                        st.rerun()
                                with col2:
                                    st.write(row["Nom du festival"])
                                with col3:
                                    st.write(row["Discipline dominante"])
                                with col4:
                                    s = row["Date de début"].strftime(
                                        "%d/%m/%Y")
                                    e = row["Date de fin"].strftime("%d/%m/%Y")
                                    st.write(f"{s} - {e}")

                with tab2:
                    layer = pdk.Layer(
                        "ScatterplotLayer", data=festivals_filtres, get_position=["lon", "lat"],
                        get_fill_color=[255, 107, 107], get_radius=10000, pickable=True,
                    )
                    view_state = pdk.ViewState(
                        latitude=festivals_filtres["lat"].mean(), longitude=festivals_filtres["lon"].mean(), zoom=5,
                    )
                    deck = pdk.Deck(
                        layers=[layer], initial_view_state=view_state,
                        tooltip={"text": "{Nom du festival}",
                                 "region": "{Région principale de déroulement}"}
                    )
                    st.pydeck_chart(deck)


# ==========================================
# 4. ITINÉRAIRE TRAIN API SNCF
# ==========================================

if selection == "recherche" and st.session_state.get("show_itinerary", False):
    st.markdown("---")
    st.title("🚄 Réservez votre trajet")

    with st.container(border=True):
        colA, colB, colC = st.columns(3)
        liste_noms = gares_df['Nom'].tolist()

        gare_auto = st.session_state["gare_arrivee_auto"]
        index_arrivee = liste_noms.index(
            gare_auto) if gare_auto in liste_noms else None

        with colA:
            ville_dep_nom = st.selectbox(
                "Départ", liste_noms, index=None, placeholder="Votre gare de départ")
        with colB:
            ville_arr_nom = st.selectbox(
                "Arrivée (Gare du festival)", liste_noms, index=index_arrivee)
        with colC:
            date_voyage = st.date_input(
                "Date du voyage", event_date_debut, format="DD/MM/YYYY")

        btn_train = st.button("Rechercher les trains",
                              use_container_width=True)

    if btn_train:
        if ville_dep_nom and ville_arr_nom:
            row_dep = gares_df[gares_df['Nom'] == ville_dep_nom].iloc[0]
            id_dep = formater_id_sncf(row_dep['Code(s) UIC'])

            row_arr = gares_df[gares_df['Nom'] == ville_arr_nom].iloc[0]
            id_arr = formater_id_sncf(row_arr['Code(s) UIC'])

            with st.spinner('Interrogation de la SNCF...'):
                journeys = get_journeys_detailed(id_dep, id_arr, date_voyage)

            if journeys:
                st.write(
                    f"### 🗓️ Trajets trouvés pour le {date_voyage.strftime('%d/%m/%Y')}")
                for journey in journeys:
                    dep_time = format_heure_affichage(
                        journey['departure_date_time'])
                    arr_time = format_heure_affichage(
                        journey['arrival_date_time'])
                    duree_sec = journey['duration']
                    duree = f"{duree_sec // 3600}h{(duree_sec % 3600) // 60:02d}"
                    nb_transfers = journey.get('nb_transfers', 0)

                    type_trajet_txt = "Direct ✨" if nb_transfers == 0 else f"{nb_transfers} corresp. 🔄"
                    titre_carte = f"**{dep_time}** ➝ **{arr_time}** | ⏱️ {duree} | {type_trajet_txt}"

                    with st.expander(titre_carte):
                        sections = journey['sections']
                        for i, section in enumerate(sections):
                            mode = section.get('type')
                            if i == 0 and mode == 'street_network':
                                continue

                            if mode == 'public_transport':
                                info = section['display_informations']
                                raw_mode = info['physical_mode']
                                num_train = info.get('headsign', '')
                                nom_mode, css_class = detecter_type_train(
                                    raw_mode)

                                dep_sec = format_heure_affichage(
                                    section['departure_date_time'])
                                arr_sec = format_heure_affichage(
                                    section['arrival_date_time'])
                                dep_place = nettoyer_nom_gare(
                                    section['from']['name'])
                                arr_place = nettoyer_nom_gare(
                                    section['to']['name'])

                                html_code = (
                                    f'<div class="trajet-card {css_class}">'
                                    f'<div class="header-train"><span class="badge badge-{css_class}">{nom_mode}</span>'
                                    f'<span class="train-num">n°{num_train}</span></div>'
                                    f'<div class="time-grid">'
                                    f'<div><div class="hour">{dep_sec}</div><div class="station-name">{dep_place}</div></div>'
                                    f'<div class="arrow-col">➝</div>'
                                    f'<div style="text-align:right;"><div class="hour">{arr_sec}</div><div class="station-name">{arr_place}</div></div>'
                                    f'</div></div>'
                                )
                                st.markdown(html_code, unsafe_allow_html=True)

                            elif mode == 'waiting':
                                duree_attente = section['duration'] // 60
                                if duree_attente > 0:
                                    st.markdown(
                                        f'<div class="correspondance">⏳ {duree_attente} min</div>', unsafe_allow_html=True)
                            elif mode == 'street_network':
                                duree_marche = section['duration'] // 60
                                if duree_marche > 0:
                                    st.markdown(
                                        f'<div class="correspondance">🚶 {duree_marche} min</div>', unsafe_allow_html=True)
            else:
                st.warning("Aucun train trouvé pour cette date/destination.")
        else:
            st.error("Sélectionnez les deux gares.")
