"""
EXEMPLE D'UTILISATION DES MODULES
Montrer comment utiliser les modules en dehors de Streamlit
"""

from datetime import datetime, timedelta
from src.modules import DataLoader, FestivalFilter, RouteOptimizer, MapVisualizer

# ============================================================================
# EXEMPLE 1: Charger les données
# ============================================================================

print("=" * 70)
print("EXEMPLE 1: Chargement des données")
print("=" * 70)

# Créer un loader
loader = DataLoader("./data")

try:
    # Charger les festivals
    festivals_df = loader.load_festivals("festivals-global-festivals-pl.csv")
    print(f"✅ {len(festivals_df)} festivals chargés")
    print(f"   Colonnes: {list(festivals_df.columns)[:5]}...")
    
    # Afficher les 3 premiers
    print("\n   Premiers festivals:")
    for idx, row in festivals_df.head(3).iterrows():
        print(f"   - {row.get('nom', 'N/A')}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# EXEMPLE 2: Filtrer par date
# ============================================================================

print("\n" + "=" * 70)
print("EXEMPLE 2: Filtrer par date")
print("=" * 70)

try:
    filter_obj = FestivalFilter(festivals_df)
    
    start = datetime(2024, 6, 1)
    end = datetime(2024, 8, 31)
    
    filtered = filter_obj.filter_by_date_range(start, end)
    print(f"✅ Festivals entre {start.date()} et {end.date()}:")
    print(f"   Trouvé: {len(filtered)} festivals")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# EXEMPLE 3: Filtrer par localisation
# ============================================================================

print("\n" + "=" * 70)
print("EXEMPLE 3: Filtrer par localisation (Paris, rayon 50 km)")
print("=" * 70)

try:
    filter_obj = FestivalFilter(festivals_df)
    
    # Coordonnées de Paris
    lat_paris = 48.8566
    lon_paris = 2.3522
    
    nearby_festivals = filter_obj.filter_by_location(
        latitude=lat_paris,
        longitude=lon_paris,
        radius_km=50
    )
    
    print(f"✅ Festivals près de Paris (rayon 50 km):")
    print(f"   Trouvé: {len(nearby_festivals)} festivals")
    
    if len(nearby_festivals) > 0:
        print("\n   Top 5 plus proches:")
        for idx, (_, row) in enumerate(nearby_festivals.head(5).iterrows()):
            dist = row.get('distance', 'N/A')
            nom = row.get('nom', 'N/A')
            print(f"   {idx+1}. {nom} ({dist:.1f} km)")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# EXEMPLE 4: Filtrage combiné
# ============================================================================

print("\n" + "=" * 70)
print("EXEMPLE 4: Filtrage combiné (date + localisation)")
print("=" * 70)

try:
    filter_obj = FestivalFilter(festivals_df)
    
    start = datetime(2024, 6, 1)
    end = datetime(2024, 8, 31)
    lat_paris = 48.8566
    lon_paris = 2.3522
    
    results = filter_obj.filter_combined(
        start_date=start,
        end_date=end,
        latitude=lat_paris,
        longitude=lon_paris,
        radius_km=100
    )
    
    print(f"✅ Festivals (Juin-Août 2024, Paris ±100km):")
    print(f"   Trouvé: {len(results)} festivals")
    
    if len(results) > 0:
        print("\n   Les 5 premiers:")
        for idx, (_, row) in enumerate(results.head(5).iterrows()):
            nom = row.get('nom', 'N/A')
            date_debut = row.get('date_debut', 'N/A')
            dist = row.get('distance', 'N/A')
            print(f"   {idx+1}. {nom}")
            print(f"      Date: {date_debut}, Distance: {dist:.1f} km")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# EXEMPLE 5: Optimiser un itinéraire
# ============================================================================

print("\n" + "=" * 70)
print("EXEMPLE 5: Optimiser un itinéraire")
print("=" * 70)

try:
    # Préparer les données
    filter_obj = FestivalFilter(festivals_df)
    results = filter_obj.filter_by_location(48.8566, 2.3522, radius_km=100)
    results = results.head(5)  # Prendre les 5 premiers
    
    # Créer l'optimiseur
    optimizer = RouteOptimizer(festivals_df, festivals_df)
    
    # Optimiser l'itinéraire
    tour = optimizer.optimize_tour(
        results.to_dict('records'),
        start_point=(48.8566, 2.3522)
    )
    
    print(f"✅ Itinéraire optimisé pour {len(tour)} festivals:")
    
    # Afficher l'ordre recommandé
    print("\n   Ordre de visite recommandé:")
    for idx, festival in enumerate(tour, 1):
        nom = festival.get('nom', 'Festival')
        print(f"   {idx}. {nom}")
    
    # Résumé de l'itinéraire
    summary = optimizer.get_route_summary(tour)
    print(f"\n   Résumé:")
    print(f"   Distance totale: {summary['total_distance']} km")
    print(f"   Distance moyenne: {summary['average_distance_between']} km")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# EXEMPLE 6: Obtenir les catégories
# ============================================================================

print("\n" + "=" * 70)
print("EXEMPLE 6: Obtenir les catégories de festivals")
print("=" * 70)

try:
    filter_obj = FestivalFilter(festivals_df)
    categories = filter_obj.get_categories()
    
    if len(categories) > 0:
        print(f"✅ {len(categories)} catégories trouvées:")
        for idx, cat in enumerate(sorted(categories)[:10], 1):
            print(f"   {idx}. {cat}")
        if len(categories) > 10:
            print(f"   ... et {len(categories) - 10} autres")
    else:
        print("⚠️  Colonne 'categorie' non trouvée dans les données")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

# ============================================================================
# RÉSUMÉ
# ============================================================================

print("\n" + "=" * 70)
print("RÉSUMÉ DES MODULES")
print("=" * 70)

print("""
✅ DataLoader
   - load_festivals()  → Charger les festivals
   - load_stations()   → Charger les gares
   - load_schedules()  → Charger les horaires

✅ FestivalFilter
   - filter_by_date_range()    → Par dates
   - filter_by_location()      → Par proximité GPS
   - filter_combined()         → Date + Localisation
   - filter_by_category()      → Par catégorie
   - get_categories()          → Lister les catégories

✅ RouteOptimizer
   - find_nearest_station()    → Gares proches
   - optimize_tour()           → Itinéraire optimal
   - get_route_summary()       → Statistiques
   - calculate_distance_between_festivals() → Distance entre 2 festivals

✅ MapVisualizer
   - create_festival_map()     → Carte festivals
   - create_stations_map()     → Carte gares
   - create_itinerary_map()    → Itinéraire complet
""")

print("=" * 70)
print("Pour plus de détails, consultez le README.md")
print("=" * 70)
