# 🎭 Application de Découverte de Festivals - Guide Complet

## 📋 Vue d'ensemble

Cette application Streamlit permet de découvrir des festivals en France et d'optimiser son itinéraire de visite en fonction de :
- **Localisation** : Rayon de recherche à partir d'une ville ou coordonnées personnalisées
- **Dates** : Plage de dates pour trouver les festivals pertinents
- **Filtres** : Envergure territoriale et autres critères

L'application propose un itinéraire optimisé entre les festivals et les gares les plus proches.

## 🗂️ Structure du projet

```
Festoches/
├── app.py                          # Application Streamlit principale
├── requirements.txt                # Dépendances Python
├── .streamlit/
│   └── config.toml                # Configuration Streamlit
├── data/                          # Dossier des données CSV
│   ├── festivals-global-festivals-pl.csv     # Données des festivals
│   ├── gares_francaises.csv       # Données des gares (à ajouter)
│   └── horaires_trains.csv        # Horaires des trains (à ajouter)
├── src/
│   ├── __init__.py
│   └── modules/
│       ├── __init__.py
│       ├── data_loader.py         # Chargement et nettoyage des données
│       ├── data_filter.py         # Filtrage des festivals
│       ├── route_optimizer.py     # Optimisation d'itinéraires
│       └── map_visualizer.py      # Visualisations cartographiques
├── README.md                       # Ce fichier
└── Main.ipynb                     # Notebook d'analyse
```

## 🚀 Installation et lancement

### 1. Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances

```bash
# Windows PowerShell
pip install -r requirements.txt

# Ou avec conda
conda install --file requirements.txt
```

### 3. Préparation des données

Placez vos fichiers CSV dans le dossier `./data/` :

- **festivals-global-festivals-pl.csv** : Doit contenir les colonnes essentielles :
  - `nom` : Nom du festival
  - `date_debut` : Date de début (format: YYYY-MM-DD)
  - `date_fin` : Date de fin (format: YYYY-MM-DD)
  - `latitude` : Latitude du festival
  - `longitude` : Longitude du festival
  - `Envergure territoriale` : Portée du festival (local, régional, national, etc.)

- **gares_francaises.csv** (optionnel) : Données des gares
  - `nom` : Nom de la gare
  - `latitude` : Latitude
  - `longitude` : Longitude

- **horaires_trains.csv** (optionnel) : Horaires des trains

### 4. Lancement de l'application

```bash
# Windows PowerShell
streamlit run app.py

# L'application s'ouvrira dans votre navigateur par défaut
# URL: http://localhost:8501
```

## 📖 Guide d'utilisation

### Panneau de contrôle (Sidebar)

1. **Localisation de départ** : Sélectionnez une ville de départ ou entrez des coordonnées personnalisées
2. **Rayon de recherche** : Ajustez le rayon en km (10-500 km)
3. **Plage de dates** : Sélectionnez les dates de votre visite
4. **Filtres** : Appliquez des filtres par envergure territoriale

### Onglets d'affichage

#### 📋 Liste
Tableau interactif avec tous les festivals trouvés, triés par distance.

#### 🗺️ Carte
Visualisation cartographique avec les marqueurs pour chaque festival.

#### 🛤️ Itinéraire
- Affiche l'ordre de visite optimisé
- Distance totale et moyenne entre festivals
- Carte avec l'itinéraire tracé

#### 📊 Statistiques
- Distribution par envergure territoriale
- Distribution des distances

## 🔧 Modules Python

### `DataLoader`
**Fichier** : `src/modules/data_loader.py`

Charge et nettoie les données :
```python
loader = DataLoader("./data")
festivals = loader.load_festivals("festivals-global-festivals-pl.csv")
stations = loader.load_stations("gares_francaises.csv")
```

### `FestivalFilter`
**Fichier** : `src/modules/data_filter.py`

Filtre les festivals selon plusieurs critères :
```python
filter_obj = FestivalFilter(festivals_df)

# Filtrer par date
festivals = filter_obj.filter_by_date_range(start_date, end_date)

# Filtrer par localisation
festivals = filter_obj.filter_by_location(latitude, longitude, radius_km=100)

# Filtrer de manière combinée
festivals = filter_obj.filter_combined(start_date, end_date, latitude, longitude, radius_km)
```

### `RouteOptimizer`
**Fichier** : `src/modules/route_optimizer.py`

Optimise les itinéraires entre festivals :
```python
optimizer = RouteOptimizer(stations_df, festivals_df)

# Optimiser la tournée
tour = optimizer.optimize_tour(festivals_list, start_point)

# Obtenir un résumé
summary = optimizer.get_route_summary(tour)
```

### `MapVisualizer`
**Fichier** : `src/modules/map_visualizer.py`

Crée des cartes interactives :
```python
visualizer = MapVisualizer()

# Carte des festivals
m = visualizer.create_festival_map(festivals_df)

# Carte avec itinéraire
m = visualizer.create_itinerary_map(festivals_df, stations_df)
```

## 📊 Exemple de données

### Format CSV festivals
```csv
nom;date_debut;date_fin;latitude;longitude;Envergure territoriale
Festival Rock Paris;2024-06-15;2024-06-17;48.8566;2.3522;National
Festival Jazz Lyon;2024-07-01;2024-07-03;45.7640;4.8357;Régional
```

## 🎯 Améliorations futures

- [ ] Intégration avec l'API SNCF pour les horaires réels
- [ ] Calcul des coûts de déplacement
- [ ] Hébergement recommandé selon la localisation
- [ ] Calendrier de saisie des événements
- [ ] Export d'itinéraires en PDF
- [ ] Synchronisation avec les calendriers (Google Calendar, Outlook)
- [ ] Recommandations personnalisées par genre musical
- [ ] Mode collaboratif pour partager des itinéraires

## 🐛 Dépannage

### Erreur : "Aucun festival ne correspond à vos critères"
- Élargissez le rayon de recherche
- Augmentez la plage de dates
- Vérifiez que vos données CSV sont correctement formatées

### Erreur : "Fichier CSV non trouvé"
- Assurez-vous que les fichiers sont dans le dossier `./data/`
- Vérifiez l'orthographe des noms de fichiers
- Utilisez les chemins relatifs correctement

### L'application se lance mais rien ne s'affiche
- Attendez le chargement complet des données (barre de progression)
- Vérifiez la console pour les messages d'erreur
- Actualisez votre navigateur

## 📝 Licence

Ce projet est fourni à titre d'exemple éducatif.

## 🤝 Contribution

Pour contribuer au projet, créez une branche et proposez vos modifications !

## 📞 Support

Pour toute question ou signalement de bug, consultez la documentation ou contactez l'équipe de développement.

---

**Dernière mise à jour** : Décembre 2024
