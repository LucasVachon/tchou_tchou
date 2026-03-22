# Structure du Projet Complet

## 📁 Arborescence du projet

```
Festoches/
│
├── 📄 app.py                          ⭐ APPLICATION PRINCIPALE
├── 📄 config.py                       ← Constantes & paramètres
├── 📄 requirements.txt                ← Dépendances (pip install)
│
├── 🔧 check_installation.py           ← Vérifier l'installation
├── 🔧 generate_sample_data.py         ← Générer des données d'exemple
├── 🔧 test_modules.py                 ← Tests unitaires
│
├── 📚 DOCUMENTATION
│   ├── README.md                      ← Guide complet
│   ├── QUICKSTART.md                  ← Démarrage rapide (3 étapes)
│   ├── INSTALLATION.md                ← Guide d'installation détaillé
│   ├── DATA_FORMAT.md                 ← Format des fichiers CSV
│   └── PROJECT_STRUCTURE.md           ← Ce fichier
│
├── 📊 data/                           ← Dossier des données
│   └── festivals-global-festivals-pl.csv  (Vous l'avez déjà !)
│
├── 🐍 src/                            ← Code source (modules)
│   ├── __init__.py
│   └── modules/
│       ├── __init__.py
│       ├── data_loader.py             ← Chargement des CSV
│       ├── data_filter.py             ← Filtrage des festivals
│       ├── route_optimizer.py         ← Optimisation itinéraires
│       └── map_visualizer.py          ← Cartes avec Folium
│
├── ⚙️ .streamlit/
│   └── config.toml                    ← Configuration Streamlit
│
├── 📓 Main.ipynb                      ← Notebook Jupyter existant
│
├── 🔐 .gitignore                      ← Fichiers à ignorer par Git
│
└── 📄 festivals-global-festivals-pl.csv  (Fichier de base)
```

## 🎯 Cas d'usage

### 1️⃣ Premier lancement (QUICKSTART.md)
```powershell
pip install -r requirements.txt
streamlit run app.py
```

### 2️⃣ Vérifier l'installation
```powershell
python check_installation.py
```

### 3️⃣ Générer des données d'exemple
```powershell
python generate_sample_data.py
```

### 4️⃣ Lancer les tests
```powershell
pytest test_modules.py -v
```

## 🔌 Modules Python

### `data_loader.py` - Chargement des données
- **Classe**: `DataLoader`
- **Méthodes principales**:
  - `load_festivals(filename)` → charge les festivals
  - `load_stations(filename)` → charge les gares
  - `load_schedules(filename)` → charge les horaires
- **Fonctionnalité**: Nettoyage automatique des données

### `data_filter.py` - Filtrage intelligent
- **Classe**: `FestivalFilter`
- **Méthodes principales**:
  - `filter_by_date_range(start, end)` → par dates
  - `filter_by_location(lat, lon, radius)` → par proximité
  - `filter_combined(...)` → combiné
  - `filter_by_category(category)` → par catégorie
- **Utilise**: Haversine pour les distances GPS

### `route_optimizer.py` - Optimisation itinéraires
- **Classe**: `RouteOptimizer`
- **Méthodes principales**:
  - `find_nearest_station(lat, lon, num)` → gares les plus proches
  - `optimize_tour(festivals, start_point)` → itinéraire optimal
  - `get_route_summary(tour)` → résumé statistique
- **Algorithme**: Glouton (nearest neighbor)

### `map_visualizer.py` - Cartographie interactive
- **Classe**: `MapVisualizer`
- **Méthodes principales**:
  - `create_festival_map(...)` → carte festivals
  - `create_stations_map(...)` → carte gares
  - `create_itinerary_map(...)` → itinéraire complet
- **Utilise**: Folium & Streamlit-Folium

## 📊 Flux de données

```
CSV files (data/)
        ↓
  DataLoader.load_*()
        ↓
  pd.DataFrame objects
        ↓
  ┌─────────────────────────────────────────┐
  │  Streamlit App (app.py)                 │
  │  ├─ Paramètres utilisateur (sidebar)   │
  │  ├─ FestivalFilter.filter_*()          │
  │  ├─ RouteOptimizer.optimize_tour()     │
  │  └─ MapVisualizer.create_*map()        │
  └─────────────────────────────────────────┘
        ↓
  Display (Tabs)
  ├─ Liste (DataFrame)
  ├─ Carte (Folium)
  ├─ Itinéraire (Path + Stats)
  └─ Statistiques (Charts)
```

## ⚙️ Fichiers de configuration

### `config.py`
- Constantes de l'application
- Listes des villes principales
- Paramètres par défaut
- Chemins des fichiers

### `.streamlit/config.toml`
- Thème personnalisé (couleurs, polices)
- Options du client Streamlit
- Options du logger

## 🧪 Tests

### Fichier: `test_modules.py`
- Tests du filtrage (`TestFestivalFilter`)
- Tests de l'optimisation (`TestRouteOptimizer`)
- Tests de la visualisation (`TestMapVisualizer`)

**Lancer les tests:**
```powershell
pytest test_modules.py -v
```

## 📋 Données requises

### Fichier obligatoire: `festivals-global-festivals-pl.csv`
Colonnes requises:
- `nom` : Nom du festival
- `date_debut` : Date de début (YYYY-MM-DD)
- `date_fin` : Date de fin (YYYY-MM-DD)
- `latitude` : Latitude (float)
- `longitude` : Longitude (float)
- `Envergure territoriale` : Local/Régional/National/International

### Fichiers optionnels
- `gares_francaises.csv` : Gares SNCF
- `horaires_trains.csv` : Horaires de trains

Voir `DATA_FORMAT.md` pour plus de détails.

## 🚀 Déploiement

### Option 1: Streamlit Cloud (gratuit)
```
1. Pusher le projet sur GitHub
2. Aller sur streamlit.io/cloud
3. Connecter le repo GitHub
4. Sélectionner le fichier app.py
```

### Option 2: Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Option 3: Heroku
- Créer un `Procfile` : `web: streamlit run app.py`
- Déployer via Git

## 🎓 Extensions possibles

- [ ] Intégration API SNCF pour les vrais horaires
- [ ] Système de recommandations ML
- [ ] Sauvegarde des itinéraires favoris
- [ ] Export en PDF/iCal
- [ ] Synchronisation Google Calendar
- [ ] Mode hors-ligne (cache)
- [ ] Multilangue
- [ ] Notifications pour les nouveaux festivals

## 📞 Support

Pour toute question :
1. Consultez `README.md` (guide complet)
2. Consultez `DATA_FORMAT.md` (format des données)
3. Lancez `check_installation.py` (diagnostic)
4. Consultez les tests dans `test_modules.py`

## 📝 Contrôle de version

Utilisez Git pour versionner :
```powershell
git init
git add .
git commit -m "Initial commit: Festival discovery app"
git remote add origin <your-repo-url>
git push -u origin main
```

Le fichier `.gitignore` est déjà configuré !

---

**Dernière mise à jour**: Décembre 2024  
**Version**: 1.0.0
