# 🎭 Application de Découverte de Festivals - Vue d'ensemble visuelle

## 🎯 Workflow utilisateur

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎭 APPLICATION STREAMLIT                     │
│                   Découverte de Festivals                        │
└─────────────────────────────────────────────────────────────────┘

1️⃣  PARAMÈTRES (Sidebar)
    ┌─────────────────────────────────────┐
    │ 📍 Localisation                     │
    │   ├─ Ville prédéfinie ↔ Perso      │
    │   └─ Rayon: 10-500 km              │
    │ 📅 Dates                           │
    │   ├─ Début                         │
    │   └─ Fin                           │
    │ 🎨 Filtres                         │
    │   └─ Envergure territoriale        │
    └─────────────────────────────────────┘
                    ↓
2️⃣  TRAITEMENT (Modules Python)
    ┌─────────────────────────────────────┐
    │ DataLoader                          │
    │ ├─ Charge festivals.csv            │
    │ ├─ Charge gares.csv               │
    │ └─ Nettoyage automatique          │
    └─────────────────────────────────────┘
                    ↓
    ┌─────────────────────────────────────┐
    │ FestivalFilter                      │
    │ ├─ Filtre par date                │
    │ ├─ Filtre par localisation        │
    │ └─ Filtre par catégorie           │
    └─────────────────────────────────────┘
                    ↓
    ┌─────────────────────────────────────┐
    │ RouteOptimizer                      │
    │ ├─ Calcule distances (Haversine)   │
    │ ├─ Optimise l'itinéraire          │
    │ └─ Génère statistiques             │
    └─────────────────────────────────────┘
                    ↓
3️⃣  AFFICHAGE (Onglets)
    ┌────────────────────────────────────────────────────┐
    │ 📋 LISTE          | 🗺️ CARTE   | 🛤️ ITINÉRAIRE | 📊 STATS │
    ├────────────────────────────────────────────────────┤
    │ • Tableau         | • Marqueurs| • Top-to-bottom | • Pie    │
    │ • Tri par dist.   | • Folium   | • Connections  | • Bars   │
    │ • Détails         | • Zoom     | • Résumé dist. | • Events │
    └────────────────────────────────────────────────────┘
```

---

## 📊 Architecture modulaire

```
┌─────────────────────────────────────────────────────────────┐
│                     app.py (Interface)                       │
│                    Streamlit Main App                        │
└────────────┬────────────────────────────────────────┬────────┘
             │                                        │
             ↓                                        ↓
    ┌─────────────────────────────────┐   ┌─────────────────────┐
    │     src/modules/                │   │   config.py         │
    │  ┌──────────────────────────┐  │   │  ┌────────────────┐ │
    │  │ data_loader.py           │  │   │  │ Villes & params│ │
    │  │ • DataLoader class       │  │   │  │ • Const France │ │
    │  │ • load_festivals()       │  │   │  │ • Thème colors │ │
    │  │ • load_stations()        │  │   │  └────────────────┘ │
    │  │ • clean_data()           │  │   └─────────────────────┘
    │  └──────────────────────────┘  │
    │  ┌──────────────────────────┐  │   ┌──────────────────────┐
    │  │ data_filter.py           │  │   │ .streamlit/          │
    │  │ • FestivalFilter class   │  │   │ config.toml          │
    │  │ • filter_by_date()       │  │   │ • Thème              │
    │  │ • filter_by_location()   │  │   │ • Options UI         │
    │  │ • filter_combined()      │  │   └──────────────────────┘
    │  └──────────────────────────┘  │
    │  ┌──────────────────────────┐  │
    │  │ route_optimizer.py       │  │
    │  │ • RouteOptimizer class   │  │
    │  │ • optimize_tour()        │  │
    │  │ • calc_distances()       │  │
    │  │ • get_summary()          │  │
    │  └──────────────────────────┘  │
    │  ┌──────────────────────────┐  │
    │  │ map_visualizer.py        │  │
    │  │ • MapVisualizer class    │  │
    │  │ • create_festival_map()  │  │
    │  │ • create_itinerary_map() │  │
    │  └──────────────────────────┘  │
    └─────────────────────────────────┘
             ↓
    ┌─────────────────────────────────┐
    │      data/ (CSV files)          │
    │  ├─ festivals.csv               │
    │  ├─ gares_francaises.csv        │
    │  └─ horaires_trains.csv         │
    └─────────────────────────────────┘
```

---

## 🔄 Flux de données

```
┌──────────────────┐
│  festivals.csv   │
│  gares.csv       │ ───┐
│  horaires.csv    │    │
└──────────────────┘    │
                        │
                        ↓
                ┌────────────────────┐
                │  DataLoader        │
                │ • Parse CSV        │
                │ • Validate data    │
                │ • Clean NaN        │
                └────────────────────┘
                        │
                        ↓
                ┌────────────────────┐
                │ pd.DataFrame       │
                │ • festivals_df     │
                │ • stations_df      │
                └────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
    ┌─────────┐   ┌──────────┐   ┌────────────┐
    │ Filter  │   │Optimizer │   │Visualizer  │
    │ by:     │   │ • Path   │   │ • Map      │
    │ • Date  │   │ • Dist   │   │ • Chart    │
    │ • Geo   │   │ • Stats  │   │ • Table    │
    └─────────┘   └──────────┘   └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ↓
                ┌────────────────────┐
                │ Streamlit UI       │
                │ • 4 Onglets        │
                │ • Sidebar          │
                │ • Interactif       │
                └────────────────────┘
                        │
                        ↓
                ┌────────────────────┐
                │ 🌐 Navigateur      │
                │ localhost:8501     │
                └────────────────────┘
```

---

## 📈 Cas d'usage simplifié

```
┌─────────────────────────────────────────────────────────────┐
│  Utilisateur cherche des festivals rock en Île-de-France    │
│  pour le mois de juillet 2024 dans un rayon de 50 km        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   📍 Paris        📅 Jul 2024   🎨 Rock
  (Sidebar)       (Sidebar)      (Filter)
        │              │              │
        └──────────────┼──────────────┘
                       ↓
            ┌──────────────────┐
            │ FestivalFilter   │
            │  • 300 → 12      │
            │ festivals match  │
            └──────────────────┘
                       ↓
            ┌──────────────────┐
            │ RouteOptimizer   │
            │  Ordre optimal:  │
            │  1. Festival A   │
            │  2. Festival G   │
            │  3. Festival M   │
            └──────────────────┘
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
    🗺️ Carte                    🛤️ Itinéraire
   (12 marqueurs)              (Ordre + Distance)
   + Zoom interactif           + Gares proches
```

---

## 🎨 Interface utilisateur (Tabs)

```
┌──────────────────────────────────────────────────────────────────┐
│ 🎭 Découverte de Festivals en France                             │
│ Explorez les festivals à proximité et planifiez votre itinéraire  │
├──────────────────────────────────────────────────────────────────┤
│ 📋 LISTE | 🗺️ CARTE | 🛤️ ITINÉRAIRE | 📊 STATISTIQUES           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TAB ACTIF: 📋 LISTE                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Détails des festivals                      [12 trouvés]    │ │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ nom             │ date_debut│ date_fin │ distance (km)  │ │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ Festival A      │ 2024-07-01│ 2024-07-05│    12.5      │ │
│  │ Festival G      │ 2024-07-15│ 2024-07-17│    24.8      │ │
│  │ Festival M      │ 2024-07-22│ 2024-07-24│    48.2      │ │
│  │ ...             │ ...       │ ...      │     ...       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Intégrations possibles

```
┌─────────────────────────────────────────────────────┐
│       Application Streamlit (Festoches)             │
└────────┬────────────────────────────────────┬───────┘
         │                                    │
         ↓                                    ↓
    ┌──────────────┐                  ┌─────────────┐
    │ API SNCF     │                  │ Google Maps │
    │ • Horaires   │                  │ • Geocoding │
    │ • Prix       │                  │ • Routing   │
    │ • Billets    │                  │             │
    └──────────────┘                  └─────────────┘
         ↑                                    ↑
         │                                    │
         └────────────┬──────────────────────┘
                      │
            ┌─────────────────────┐
            │ À implémenter       │
            │ (Extensions futures)│
            └─────────────────────┘
```

---

## 📦 Packaging et déploiement

```
                 Festoches/
                     │
        ┌────────────┼────────────┐
        │            │            │
        ↓            ↓            ↓
    📁 Local     🐳 Docker    ☁️ Cloud
    ┌─────┐    ┌───────┐   ┌─────────┐
    │Pip  │    │Image  │   │Streamlit│
    │Env  │    │Deploy │   │Cloud    │
    └─────┘    └───────┘   └─────────┘
```

---

## 🧪 Teste & QA

```
┌─────────────────────────────────────┐
│        test_modules.py              │
├─────────────────────────────────────┤
│ TestFestivalFilter                  │
│ ├─ test_filter_by_date_range       │
│ ├─ test_filter_by_location         │
│ └─ test_get_categories             │
│                                     │
│ TestRouteOptimizer                  │
│ ├─ test_optimize_tour              │
│ └─ test_get_route_summary          │
│                                     │
│ TestMapVisualizer                   │
│ └─ test_create_festival_map        │
└─────────────────────────────────────┘
         │
         ↓
    pytest run
         │
         ↓
    ✅ All tests pass
```

---

## 🎓 Courbe d'apprentissage

```
Débutant          Intermédiaire         Expert
    │                 │                    │
    ├─ Lancer app    ├─ Modifier data   ├─ Ajouter API
    ├─ Utiliser UI   ├─ Ajouter filtres ├─ Déployer
    └─ Voir résult.  ├─ Changer thème   ├─ Optimiser
                     └─ Écrire tests    └─ ML/Advanced
```

---

## ✅ Checklist d'utilisation

- [ ] `pip install -r requirements.txt`
- [ ] `python check_installation.py`
- [ ] Vérifier les données dans `data/`
- [ ] `streamlit run app.py`
- [ ] Tester les 4 onglets
- [ ] Modifier les filtres
- [ ] Lire la documentation
- [ ] Déployer en production

---

**Créé avec ❤️ pour les amateurs de festivals !**
