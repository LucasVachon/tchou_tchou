import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Train Festival SNCF",
    page_icon="🚄",
    layout="wide"
)

# Chargement des variables
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")
BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
CSV_PATH = "gares-de-voyageurs.csv"

# ==========================================
# 0. STYLE CSS (GRILLE & COMPACITÉ)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* --- Styles des Cartes --- */
        .trajet-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 10px 15px; 
            margin-bottom: 8px;
            border-left: 5px solid #ccc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .trajet-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        }

        /* --- Couleurs --- */
        .tgv { border-left-color: #9b59b6; background-color: #fcf4ff; }
        .ter { border-left-color: #3498db; background-color: #f0f8ff; }
        .intercites { border-left-color: #27ae60; background-color: #effcf5; }
        .autocar { border-left-color: #FF9F43; background-color: #FFF6EA; } /* Orange Bus */
        
        /* --- Header (Badge + Nom) --- */
        .header-train { 
            display: flex; 
            align-items: center; 
            margin-bottom: 6px; 
        }
        .badge { 
            padding: 3px 8px;
            border-radius: 4px; 
            color: white; 
            font-weight: bold;
            font-size: 0.75em; 
            margin-right: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-tgv { background-color: #9b59b6; }
        .badge-ter { background-color: #3498db; }
        .badge-intercites { background-color: #27ae60; }
        .badge-autocar { background-color: #FF9F43; }
        .badge-other { background-color: #95a5a6; }

        .train-num {
            color: #7f8c8d;
            font-weight: 500;
            font-size: 0.8em;
        }

        /* --- GRILLE --- */
        .time-grid { 
            display: grid;
            grid-template-columns: 1fr 40px 1fr; 
            align-items: center; 
        }
        
        .time-grid > div:last-child {
            text-align: right;
        }

        .arrow-col {
            text-align: center;
            color: #bdc3c7;
            font-size: 1.2em;
            margin-top: -5px; 
        }
        
        .hour { 
            font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 1.2em; 
            font-weight: 700; 
            color: #2c3e50; 
            line-height: 1;
        }
        
        .station-name { 
            font-size: 0.85em;
            color: #576574; 
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* --- Correspondances --- */
        .correspondance {
            text-align: center;
            color: #95a5a6;
            font-size: 0.8em;
            margin: 4px 0;
            font-style: italic;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .correspondance::before, .correspondance::after {
            content: "";
            flex: 1;
            border-bottom: 1px dashed #e0e0e0;
            margin: 0 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. FONCTIONS BACKEND
# ==========================================

@st.cache_data
def charger_gares(chemin_csv):
    try:
        df = pd.read_csv(chemin_csv, sep=';', dtype={'Code(s) UIC': str})
        df = df.dropna(subset=['Nom']).drop_duplicates(subset=['Nom'])
        return df.sort_values('Nom')
    except FileNotFoundError:
        st.error(f"❌ Le fichier '{chemin_csv}' est introuvable.")
        return None

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
    params = {
        'from': id_dep,
        'to': id_arr,
        'datetime': date_str_api,
        'min_nb_journeys': 20 
    }

    try:
        response = requests.get(url, params=params, auth=(API_KEY, ''))
        response.raise_for_status()
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None

    data = response.json()
    
    if 'journeys' not in data:
        return []

    journeys_filtrés = []
    for journey in data['journeys']:
        if journey['departure_date_time'][:8] == date_filter:
            journeys_filtrés.append(journey)
            
    return journeys_filtrés

# ==========================================
# 2. INTERFACE STREAMLIT
# ==========================================

local_css()
st.title("🚄 Recherche de Trains - Festival")

df_gares = charger_gares(CSV_PATH)

if df_gares is not None:
    
    # --- ZONE DE RECHERCHE ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        liste_noms = df_gares['Nom'].tolist()
        
        with col1:
            ville_dep_nom = st.selectbox("Départ", liste_noms, index=None, placeholder="Gare de départ")
        with col2:
            ville_arr_nom = st.selectbox("Arrivée", liste_noms, index=None, placeholder="Gare d'arrivée")
        with col3:
            date_voyage = st.date_input("Date", datetime.now(), format="DD/MM/YYYY")

        btn_search = st.button("Rechercher les trajets", use_container_width=True)

    # --- RESULTATS ---
    if btn_search:
        if ville_dep_nom and ville_arr_nom:
            row_dep = df_gares[df_gares['Nom'] == ville_dep_nom].iloc[0]
            id_dep = formater_id_sncf(row_dep['Code(s) UIC'])
            
            row_arr = df_gares[df_gares['Nom'] == ville_arr_nom].iloc[0]
            id_arr = formater_id_sncf(row_arr['Code(s) UIC'])

            with st.spinner('Interrogation de la SNCF...'):
                journeys = get_journeys_detailed(id_dep, id_arr, date_voyage)

            if journeys:
                st.write(f"### 🗓️ Trajets pour le {date_voyage.strftime('%d/%m/%Y')}")
                st.markdown("---")

                for journey in journeys:
                    # Infos Globales
                    dep_time = format_heure_affichage(journey['departure_date_time'])
                    arr_time = format_heure_affichage(journey['arrival_date_time'])
                    duree_sec = journey['duration']
                    duree = f"{duree_sec // 3600}h{(duree_sec % 3600) // 60:02d}"
                    nb_transfers = journey.get('nb_transfers', 0)
                    
                    if nb_transfers == 0:
                        type_trajet_txt = "Direct ✨"
                    else:
                        type_trajet_txt = f"{nb_transfers} corresp. 🔄"

                    titre_carte = f"**{dep_time}** ➝ **{arr_time}** | ⏱️ {duree} | {type_trajet_txt}"
                    
                    # --- DEBUT DE L'EXPANDER ---
                    with st.expander(titre_carte):
                        sections = journey['sections']
                        
                        for i, section in enumerate(sections):
                            mode = section.get('type')
                            
                            if i == 0 and mode == 'street_network':
                                continue

                            # 1. TRANSPORT (Train / Bus)
                            if mode == 'public_transport':
                                info = section['display_informations']
                                raw_mode = info['physical_mode']
                                num_train = info.get('headsign', '')
                                
                                nom_mode, css_class = detecter_type_train(raw_mode)
                                
                                dep_sec = format_heure_affichage(section['departure_date_time'])
                                arr_sec = format_heure_affichage(section['arrival_date_time'])
                                dep_place = nettoyer_nom_gare(section['from']['name'])
                                arr_place = nettoyer_nom_gare(section['to']['name'])

                                # CORRECTION : J'ai retiré 'textwrap' et j'ai collé le HTML à gauche
                                # C'est la méthode la plus sûre pour éviter les bugs d'affichage
                                html_code = f"""
<div class="trajet-card {css_class}">
    <div class="header-train">
        <span class="badge badge-{css_class}">{nom_mode}</span>
        <span class="train-num">n°{num_train}</span>
    </div>
    <div class="time-grid">
        <div>
            <div class="hour">{dep_sec}</div>
            <div class="station-name">{dep_place}</div>
        </div>
        <div class="arrow-col">➝</div>
        <div>
            <div class="hour">{arr_sec}</div>
            <div class="station-name">{arr_place}</div>
        </div>
    </div>
</div>
"""
                                st.markdown(html_code, unsafe_allow_html=True)

                            # 2. CORRESPONDANCE
                            elif mode == 'waiting':
                                duree_attente = section['duration'] // 60
                                if duree_attente > 0:
                                    st.markdown(f'<div class="correspondance">⏳ {duree_attente} min</div>', unsafe_allow_html=True)
                            
                            # 3. MARCHE
                            elif mode == 'street_network':
                                duree_marche = section['duration'] // 60
                                if duree_marche > 0:
                                    st.markdown(f'<div class="correspondance">🚶 {duree_marche} min</div>', unsafe_allow_html=True)

            else:
                st.warning("Aucun train trouvé.")
        else:
            st.error("Sélectionnez les deux gares.")