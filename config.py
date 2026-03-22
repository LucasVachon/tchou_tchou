"""
Fichier de configuration pour les constantes de l'application
"""

# Villes principales de France avec leurs coordonnées
VILLES_FRANCE = {
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
    "Montpellier": (43.6108, 3.8767),
    "Amiens": (49.8941, 2.2959),
    "Dijon": (47.3220, 5.0344),
    "Toulon": (43.1242, 5.9280),
    "Grenoble": (45.1885, 5.7245),
}

# Paramètres par défaut
DEFAULT_RADIUS_KM = 150
DEFAULT_ZOOM_LEVEL = 6
DEFAULT_CENTER_FRANCE = (46.5, 2.2)  # Centre approximatif de la France

# Chemins des fichiers de données
DATA_DIR = "./data"
FESTIVALS_FILE = "festivals-global-festivals-pl.csv"
STATIONS_FILE = "gares_francaises.csv"
SCHEDULES_FILE = "horaires_trains.csv"

# Colonnes essentielles requises
REQUIRED_FESTIVAL_COLUMNS = ['nom', 'date_debut', 'date_fin', 'latitude', 'longitude']
REQUIRED_STATION_COLUMNS = ['nom', 'latitude', 'longitude']

# Thème Streamlit
THEME_COLOR_PRIMARY = "#FF6B6B"
THEME_COLOR_SECONDARY = "#E8EAEF"
THEME_COLOR_TEXT = "#262730"

# Messages de l'application
MSG_NO_FESTIVALS = "❌ Aucun festival ne correspond à vos critères. Essayez d'élargir votre recherche."
MSG_LOADING_DATA = "⏳ Chargement des données..."
MSG_ERROR_LOADING = "❌ Erreur lors du chargement des données"
