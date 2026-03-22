"""
Application Streamlit - Découverte de Festivals avec Itinéraires Optimisés et Trains
Version 2.0 : Support complet des itinéraires de trains
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter le répertoire src au chemin
sys.path.insert(0, str(Path(__file__).parent))

from src.modules import DataLoader, FestivalFilter, RouteOptimizer, MapVisualizer, TrainJourneyPlanner
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(
    page_title="Découverte de Festivals 🎭",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
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

# Titre
st.markdown("<h1 class='main-title'>🎭 Découverte de Festivals en France</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Explorez les festivals à proximité et planifiez votre itinéraire optimal en train</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FF9800; font-size: 14px;'><b>📅 Données 2019 - Simulation historique</b></p>", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.loader = None
    st.session_state.festivals_df = None
    st.session_state.stations_df = None

# Charger les données
with st.spinner("⏳ Chargement des données..."):
    try:
        loader = DataLoader("./data")
        
        # Charger les données
        festivals_df = loader.load_festivals("festivals-global-festivals-pl.csv")
        
        # Note : les autres fichiers seront chargés s'ils existent
        try:
            stations_df = loader.load_stations("gares-de-voyageurs.csv")
        except:
            stations_df = pd.DataFrame()  # DataFrame vide si le fichier n'existe pas
        
        try:
            gare_hours_df = loader.load_gare_hours("horaires-des-gares1.csv")
        except:
            gare_hours_df = pd.DataFrame()
        
        try:
            train_schedules_df = loader.load_train_schedules("horaires-sncf.csv")
        except:
            train_schedules_df = pd.DataFrame()
        
        st.session_state.data_loaded = True
        st.session_state.festivals_df = festivals_df
        st.session_state.stations_df = stations_df
        st.session_state.gare_hours_df = gare_hours_df
        st.session_state.train_schedules_df = train_schedules_df
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        st.info("📌 Assurez-vous que les fichiers CSV sont dans le dossier `./data/`")
        st.stop()

# Afficher les statistiques des données chargées
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📅 Festivals", len(st.session_state.festivals_df))
with col2:
    if len(st.session_state.stations_df) > 0:
        st.metric("🚂 Gares", len(st.session_state.stations_df))
    else:
        st.metric("🚂 Gares", "Non chargées")
with col3:
    st.metric("📍 Régions", len(st.session_state.festivals_df.get('Envergure territoriale', pd.Series()).unique()) if 'Envergure territoriale' in st.session_state.festivals_df.columns else 0)

st.divider()

# Panneau de contrôle latéral
st.sidebar.title("⚙️ Mode de recherche")

# SÉLECTION DU MODE DE RECHERCHE
mode_recherche = st.sidebar.radio(
    "Choisissez votre mode",
    ["🗺️ Par localisation", "🚂 Par itinéraire train"],
    help="Sélectionnez comment vous souhaitez chercher des festivals"
)

st.sidebar.divider()

# ================================================================================
# MODE 1: RECHERCHE PAR LOCALISATION
# ================================================================================
if mode_recherche == "🗺️ Par localisation":
    
    st.sidebar.subheader("📍 Localisation de départ")
    
    villes_france = {
        "Paris": (48.8566, 2.3522),
        "Lyon": (45.7640, 4.8357),
        "Marseille": (43.2965, 5.3698),
        "Toulouse": (43.6047, 1.4442),
        "Nice": (43.7102, 7.2620),
        "Bordeaux": (44.8378, -0.5792),
        "Lille": (50.6292, 3.0573),
        "Nantes": (47.2184, -1.5536),
        "Strasbourg": (48.5734, 7.7521),
        "Rennes": (48.1113, -1.6800),
    }
    
    ville_selectionnee = st.sidebar.selectbox("Sélectionnez une ville", list(villes_france.keys()), key="ville_loc")
    lat_depart, lon_depart = villes_france[ville_selectionnee]
    
    if st.sidebar.checkbox("🗺️ Coordonnées personnalisées"):
        col1, col2 = st.sidebar.columns(2)
        with col1:
            lat_depart = st.number_input("Latitude", value=lat_depart, format="%.4f")
        with col2:
            lon_depart = st.number_input("Longitude", value=lon_depart, format="%.4f")
    
    rayon_km = st.sidebar.slider("Rayon (km)", 10, 500, 150, 10)
    
    st.sidebar.subheader("📅 Plage de dates")
    today = datetime(2019, 6, 1)  # Référence: été 2019
    date_debut = st.sidebar.date_input("Début", value=today, min_value=datetime(2019, 1, 1).date(), key="date_debut_loc")
    date_fin = st.sidebar.date_input("Fin", value=today + timedelta(days=90), min_value=date_debut, key="date_fin_loc")
    
    st.sidebar.subheader("🎨 Filtres")
    envergure_options = ["Tous"]
    if 'Envergure territoriale' in st.session_state.festivals_df.columns:
        envergure_options.extend(st.session_state.festivals_df['Envergure territoriale'].unique().tolist())
    envergure_selectionnee = st.sidebar.selectbox("Envergure", envergure_options, key="envergure_loc")
    
    # Appliquer les filtres
    filter_obj = FestivalFilter(st.session_state.festivals_df)
    
    # Filtrer par date (si les dates sont disponibles, sinon retourner tous)
    try:
        festivals_filtres = filter_obj.filter_by_date_range(
            datetime.combine(date_debut, datetime.min.time()),
            datetime.combine(date_fin, datetime.max.time())
        )
    except:
        # Si les dates ne sont pas disponibles, utiliser tous les festivals
        festivals_filtres = st.session_state.festivals_df.copy()
    
    if len(festivals_filtres) > 0:
        festivals_filtres = filter_obj.filter_by_location(lat_depart, lon_depart, rayon_km)
    
    if envergure_selectionnee != "Tous" and 'Envergure territoriale' in festivals_filtres.columns:
        festivals_filtres = festivals_filtres[festivals_filtres['Envergure territoriale'].notna()]
        festivals_filtres = festivals_filtres[festivals_filtres['Envergure territoriale'] == envergure_selectionnee]
    
    # Affichage des résultats
    st.subheader(f"🎵 {len(festivals_filtres)} festivals trouvés")
    
    if len(festivals_filtres) == 0:
        st.warning("❌ Aucun festival ne correspond à vos critères.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "🗺️ Carte", "🛤️ Itinéraire", "📊 Statistiques"])
        
        with tab1:
            st.subheader("Détails des festivals")
            display_cols = ['nom', 'distance']
            if 'Discipline dominante' in festivals_filtres.columns:
                display_cols.append('Discipline dominante')
            available_cols = [col for col in display_cols if col in festivals_filtres.columns]
            
            if available_cols:
                st.dataframe(festivals_filtres[available_cols].sort_values('distance'), use_container_width=True)
            else:
                st.dataframe(festivals_filtres, use_container_width=True)
        
        with tab2:
            st.subheader("Localisation des festivals")
            map_viz = MapVisualizer()
            m = map_viz.create_festival_map(festivals_filtres, center_lat=lat_depart, center_lon=lon_depart)
            st_folium(m, width=1400, height=600)
        
        with tab3:
            st.subheader("Itinéraire optimisé")
            
            if len(festivals_filtres) > 1:
                optimizer = RouteOptimizer(st.session_state.stations_df, st.session_state.festivals_df)
                tour = optimizer.optimize_tour(festivals_filtres.to_dict('records'), start_point=(lat_depart, lon_depart))
                route_summary = optimizer.get_route_summary(tour)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Distance totale", f"{route_summary['total_distance']} km")
                with col2:
                    st.metric("Festivals", route_summary['num_festivals'])
                with col3:
                    st.metric("Moyenne", f"{route_summary['average_distance_between']} km")
                
                st.divider()
                st.write("**Ordre de visite recommandé :**")
                for i, festival in enumerate(tour, 1):
                    st.write(f"{i}. **{festival.get('nom', 'Festival')}**")
                
                map_viz = MapVisualizer()
                tour_df = pd.DataFrame(tour)
                m = map_viz.create_itinerary_map(tour_df, center_lat=lat_depart, center_lon=lon_depart)
                st_folium(m, width=1400, height=600)
            else:
                st.info("Un seul festival trouvé.")
        
        with tab4:
            st.subheader("Statistiques")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Envergure territoriale' in festivals_filtres.columns:
                    st.bar_chart(festivals_filtres['Envergure territoriale'].value_counts())
            with col2:
                if 'distance' in festivals_filtres.columns:
                    st.bar_chart(festivals_filtres['distance'].value_counts().sort_index().head(20))

# ================================================================================
# MODE 2: RECHERCHE PAR ITINÉRAIRE TRAIN
# ================================================================================
else:
    
    if len(st.session_state.stations_df) == 0:
        st.error("❌ Les données des gares ne sont pas chargées. Veuillez ajouter 'gares-de-voyageurs.csv'")
    else:
        st.sidebar.subheader("🏠 Votre localisation")
        
        villes_france = {
            "Paris": (48.8566, 2.3522),
            "Lyon": (45.7640, 4.8357),
            "Marseille": (43.2965, 5.3698),
            "Toulouse": (43.6047, 1.4442),
            "Nice": (43.7102, 7.2620),
            "Bordeaux": (44.8378, -0.5792),
            "Lille": (50.6292, 3.0573),
            "Nantes": (47.2184, -1.5536),
            "Strasbourg": (48.5734, 7.7521),
            "Rennes": (48.1113, -1.6800),
        }
        
        ville_depart = st.sidebar.selectbox("Où habitez-vous ?", list(villes_france.keys()), key="ville_train")
        lat_home, lon_home = villes_france[ville_depart]
        
        st.sidebar.subheader("🚆 Vos disponibilités")
        
        col1, col2 = st.sidebar.columns([1, 2])
        with col1:
            heure_depart = st.time_input("Départ à", value=datetime.strptime("18:00", "%H:%M").time(), key="heure_dep")
        with col2:
            date_depart = st.date_input("Le", value=datetime(2019, 7, 12).date(), key="date_train_depart", min_value=datetime(2019, 1, 1).date(), max_value=datetime(2019, 12, 31).date())
        
        col1, col2 = st.sidebar.columns([1, 2])
        with col1:
            heure_retour = st.time_input("Retour avant", value=datetime.strptime("20:00", "%H:%M").time(), key="heure_ret")
        with col2:
            date_retour = st.date_input("Le", value=datetime(2019, 7, 14).date(), key="date_train_retour", min_value=date_depart, max_value=datetime(2019, 12, 31).date())
        
        st.sidebar.subheader("⚙️ Paramètres")
        max_travel_time = st.sidebar.slider("Temps de trajet max (h)", 2, 12, 6, key="max_travel")
        
        # Convertir en datetime
        dt_depart = datetime.combine(date_depart, heure_depart)
        dt_retour = datetime.combine(date_retour, heure_retour)
        
        # Créer le planificateur
        planner = TrainJourneyPlanner(
            st.session_state.stations_df,
            st.session_state.train_schedules_df,
            st.session_state.gare_hours_df,
            st.session_state.festivals_df
        )
        
        # Afficher la situation
        st.write("### 📍 Votre situation")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Ville :** {ville_depart}")
        with col2:
            st.write(f"**Départ :** {dt_depart.strftime('%d/%m à %H:%M')}")
        with col3:
            st.write(f"**Retour :** {dt_retour.strftime('%d/%m à %H:%M')}")
        
        st.divider()
        
        # Trouver les gares les plus proches
        gares_proches = planner.find_nearest_stations(lat_home, lon_home, num_stations=5)
        
        if len(gares_proches) == 0:
            st.error("❌ Impossible de trouver des gares proches")
        else:
            st.write("### 🚂 Gares les plus proches")
            
            # Obtenir le nom de colonne correct
            col_name = 'Nom' if 'Nom' in gares_proches.columns else gares_proches.columns[0]
            
            gare_depart_name = st.selectbox(
                "Sélectionnez votre gare de départ",
                gares_proches[col_name].tolist(),
                key="gare_depart_select"
            )
            
            st.divider()
            
            # Trouver les festivals accessibles
            festivals_accessibles = planner.find_festivals_accessible(
                departure_station_name=gare_depart_name,
                departure_time=dt_depart,
                return_time=dt_retour,
                max_travel_time_hours=max_travel_time
            )
            
            st.write(f"### 🎭 Festivals accessibles : {len(festivals_accessibles)}")
            
            if len(festivals_accessibles) == 0:
                st.warning("❌ Aucun festival ne correspond à vos critères.")
                st.info("💡 Conseil : Augmentez le temps de voyage ou la plage de dates")
            else:
                tab1, tab2, tab3 = st.tabs(["📋 Liste", "🗺️ Carte", "📊 Détails"])
                
                with tab1:
                    display_cols = ['nom', 'distance_km']
                    if 'Discipline dominante' in festivals_accessibles.columns:
                        display_cols.append('Discipline dominante')
                    available_cols = [col for col in display_cols if col in festivals_accessibles.columns]
                    
                    if available_cols:
                        df_display = festivals_accessibles[available_cols].sort_values('distance_km')
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.dataframe(festivals_accessibles, use_container_width=True)
                
                with tab2:
                    map_viz = MapVisualizer()
                    m = map_viz.create_festival_map(festivals_accessibles, center_lat=lat_home, center_lon=lon_home)
                    st_folium(m, width=1400, height=600)
                
                with tab3:
                    st.subheader("Détails des trajets")
                    for idx, (_, festival) in enumerate(festivals_accessibles.iterrows(), 1):
                        with st.expander(f"🎵 {festival.get('nom', 'Festival')} - {festival.get('distance_km', 0):.0f} km"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Dates**")
                                st.write(f"Début : {festival.get('date_debut', 'N/A')}")
                                st.write(f"Fin : {festival.get('date_fin', 'N/A')}")
                            
                            with col2:
                                st.write("**Distance**")
                                st.write(f"{festival.get('distance_km', 0):.0f} km")
                                st.write(f"~{max(1, int(festival.get('distance_km', 0) / 100))} h train")
                            
                            with col3:
                                st.write("**Envergure**")
                                st.write(festival.get('Envergure territoriale', 'N/A'))
