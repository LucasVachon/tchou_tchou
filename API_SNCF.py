import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# ==========================================
# CONFIGURATION
# ==========================================
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")
BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
CSV_PATH = "gares-de-voyageurs.csv"


pd.set_option('display.max_rows', None)

# ==========================================
# 1. GESTION DU CSV ET RECHERCHE
# ==========================================

def charger_gares(chemin_csv):
    try:
        df = pd.read_csv(chemin_csv, sep=';', dtype={'Code(s) UIC': str})
        return df
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{chemin_csv}' est introuvable.")
        return None

def formater_id_sncf(code_uic):
    code = str(code_uic).split(';')[0].strip()
    return f"stop_area:SNCF:{code}"

def chercher_gare_interactive(nom_saisi, df_gares):
    if df_gares is None: return None
    
    match_exact = df_gares[df_gares['Nom'].str.lower() == nom_saisi.lower()]
    if len(match_exact) == 1:
        gare = match_exact.iloc[0]
        print(f"✅ Gare trouvée (Exact) : {gare['Nom']}")
        return formater_id_sncf(gare['Code(s) UIC'])

    # 2. Recherche partielle
    mask = df_gares['Nom'].str.contains(nom_saisi, case=False, na=False)
    resultats = df_gares[mask]
    
    nb_res = len(resultats)
    
    if nb_res == 0:
        print(f"❌ Aucune gare trouvée pour '{nom_saisi}'.")
        return None
    elif nb_res == 1:
        gare = resultats.iloc[0]
        print(f"✅ Gare trouvée : {gare['Nom']}")
        return formater_id_sncf(gare['Code(s) UIC'])
    else:
        print(f"\n⚠️ Plusieurs choix pour '{nom_saisi}' :")
        for i, (idx, row) in enumerate(resultats.head(15).iterrows()):
            print(f"   [{i+1}] {row['Nom']}")
            
        try:
            choix = input(f"👉 Tapez le numéro (1-{min(nb_res, 15)}) : ")
            if choix.isdigit() and 1 <= int(choix) <= min(nb_res, 15):
                gare = resultats.iloc[int(choix)-1]
                print(f"✅ Sélectionné : {gare['Nom']}")
                return formater_id_sncf(gare['Code(s) UIC'])
            else:
                return None
        except:
            return None

# ==========================================
# 2. FONCTIONS API
# ==========================================

def format_heure(str_date):
    dt = datetime.strptime(str_date, "%Y%m%dT%H%M%S")
    return dt.strftime("%H:%M")

def convert_input_date(date_user):
    try:
        dt = datetime.strptime(date_user, "%d/%m/%Y")
        return dt.strftime("%Y%m%dT000000"), dt.strftime("%Y%m%d")
    except ValueError:
        now = datetime.now()
        return now.strftime("%Y%m%dT%H%M%S"), now.strftime("%Y%m%d")

def get_journeys_csv(id_dep, id_arr, date_input):
    date_start_api, date_filter = convert_input_date(date_input)

    url = f"{BASE_URL}/journeys"
    params = {
        'from': id_dep,
        'to': id_arr,
        'datetime': date_start_api,
        'min_nb_journeys': 100 
    }

    print("⏳ Récupération des données SNCF...")
    try:
        response = requests.get(url, params=params, auth=(API_KEY, ''))
    except Exception as e:
        print(f"Erreur connexion : {e}")
        return None

    data = response.json()
    liste_trains = []
    
    for journey in data.get('journeys', []):
        departure_full = journey['departure_date_time']

        if departure_full[:8] != date_filter:
            break 
        
        heure_dep = format_heure(departure_full)
        heure_arr = format_heure(journey['arrival_date_time'])
        duree_sec = journey['duration']
        duree = f"{duree_sec // 3600}h{(duree_sec % 3600) // 60:02d}"
        
        nb_transfers = journey.get('nb_transfers', 0)
        trajet_type = "Direct" if nb_transfers == 0 else f"{nb_transfers} correspondance(s)"

        liste_trains.append({
            "Départ": heure_dep,
            "Arrivée": heure_arr,
            "Durée": duree,
            "Type": trajet_type
        })

    if liste_trains:
        df = pd.DataFrame(liste_trains)
        print("\n" + "="*45)
        print(f"📅 HORAIRES POUR LE : {date_input}")
        print("="*45)
        print(df.to_string(index=False))
        print("="*45)
        print(f"✅ Nombre de trains trouvés : {len(liste_trains)}")
        
        return df
    else:
        print("❌ Aucun train trouvé.")
        return None

# ==========================================
# 3. LANCEMENT DU PROGRAMME
# ==========================================

df_gares = charger_gares(CSV_PATH)

if df_gares is not None:
    print("\n--- 🚅 RECHERCHE SNCF 🚅 ---")
    
    ville_dep = input("Ville de départ : ")
    id_dep = chercher_gare_interactive(ville_dep, df_gares)
    
    if id_dep:
        ville_arr = input("Ville d'arrivée : ")
        id_arr = chercher_gare_interactive(ville_arr, df_gares)
        
        if id_arr:
            date_v = input("Date (JJ/MM/AAAA) : ")
            df_final = get_journeys_csv(id_dep, id_arr, date_v)

# Stockage des résulats dans df_final