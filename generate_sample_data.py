#!/usr/bin/env python
"""
Script pour générer des données d'exemple pour l'application
Crée des fichiers CSV de test dans le dossier data/
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# Villes françaises avec leurs coordonnées
villes = {
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

genres = ["Rock", "Jazz", "Classique", "Hip-hop", "Électronique", "Folk", "Pop", "Metal", "Reggae", "Blues"]
envergures = ["Local", "Régional", "National", "International"]

# Générer des festivals
festivals = []
for i in range(100):
    ville = random.choice(list(villes.keys()))
    lat, lon = villes[ville]
    
    # Ajouter du bruit aux coordonnées
    lat += random.uniform(-0.5, 0.5)
    lon += random.uniform(-0.5, 0.5)
    
    start_date = datetime(2024, 6, 1) + timedelta(days=random.randint(0, 120))
    end_date = start_date + timedelta(days=random.randint(1, 4))
    
    festivals.append({
        'nom': f"Festival {random.choice(genres)} {ville} {i+1}",
        'date_debut': start_date.strftime("%Y-%m-%d"),
        'date_fin': end_date.strftime("%Y-%m-%d"),
        'latitude': lat,
        'longitude': lon,
        'ville': ville,
        'genre': random.choice(genres),
        'Envergure territoriale': random.choice(envergures),
        'capacite': random.randint(5000, 100000)
    })

festivals_df = pd.DataFrame(festivals)

# Générer des gares
gares = []
for ville, (lat, lon) in villes.items():
    gares.append({
        'nom': f"Gare de {ville}",
        'ville': ville,
        'latitude': lat,
        'longitude': lon
    })

gares_df = pd.DataFrame(gares)

# Sauvegarder les fichiers
import os
os.makedirs("data", exist_ok=True)

festivals_df.to_csv("data/exemple_festivals.csv", sep=";", index=False, encoding="utf-8")
gares_df.to_csv("data/exemple_gares_francaises.csv", sep=";", index=False, encoding="utf-8")

print("✅ Fichiers d'exemple créés:")
print(f"   - data/exemple_festivals.csv ({len(festivals_df)} festivals)")
print(f"   - data/exemple_gares_francaises.csv ({len(gares_df)} gares)")
print("\nPour utiliser ces fichiers d'exemple, renommez-les ou modifiez app.py pour les charger.")
