# 🎭 Application Festoches - Status de Déploiement

## ✅ Application en Production

### Lancement
```bash
cd c:\Users\Administrator\Documents\Festoches
streamlit run app.py
```

**URL locale:** http://localhost:8501

---

## 📋 Fonctionnalités Implémentées

### Mode 1: 🗺️ Par Localisation (ACTIF)
Recherche les festivals proches d'une ville ou d'une localisation personnalisée.

**Paramètres:**
- Sélection de ville (Paris, Lyon, Marseille, Rennes, etc.)
- Coordonnées personnalisées (latitude/longitude)
- Rayon de recherche: 10-500 km
- Plage de dates
- Filtrage par envergure

**Résultats:** 
- 📋 Liste des festivals avec distance
- 🗺️ Carte interactive Folium
- 🛤️ Itinéraire optimisé (algorithme greedy)
- 📊 Statistiques et distribution

**Données chargées:**
- ✅ 7138 festivals français
- ✅ Coordonnées (latitude/longitude)
- ✅ Discipline dominante
- ✅ Envergure territoriale

---

### Mode 2: 🚂 Par Itinéraire Train (ACTIF)
Planifie un itinéraire de train et trouve les festivals accessibles.

**Scénario implémenté:** Rennes → Festivals → Retour

**Paramètres:**
- Sélection de ville d'habitation (Rennes défaut)
- Date et heure de départ (défaut: 18:00 demain)
- Date et heure de retour (défaut: 20:00 surlendemain)
- Temps de trajet maximum en train: 2-12 heures

**Workflow:**
1. Find nearest stations from home city
2. Select departure station
3. Find accessible festivals based on travel time
4. Display itinerary details

**Données chargées:**
- ✅ 2778 gares françaises avec coordonnées
- ✅ Horaires d'ouverture des gares (horaires-des-gares1.csv)
- ✅ Références SNCF (horaires-sncf.csv)

**Résultats:**
- 📋 Liste des festivals accessibles
- 🗺️ Carte avec localisation des festivals
- 📊 Détails des trajets (distance, temps estimé)

---

## 🔧 Architecture Technique

### Structure Modulaire
```
src/modules/
├── __init__.py
├── data_loader.py           # Chargement des CSV
├── data_filter.py           # Filtrage des données
├── route_optimizer.py       # Optimisation d'itinéraires
├── map_visualizer.py        # Visualisations Folium
└── train_journey_planner.py # Planificateur de trains (NEW)
```

### Données CSV Intégrées
- `festivals-global-festivals-pl.csv` (7138 festivals)
- `gares-de-voyageurs.csv` (2778 stations)
- `horaires-des-gares1.csv` (6519 horaires)
- `horaires-sncf.csv` (références SNCF)

### Dépendances Python
```
streamlit==1.28.1
pandas==2.1.3
folium
streamlit-folium
haversine==2.8.0
scikit-learn==1.3.2
```

---

## 🚀 Utilisation Rapide

### Mode Location (Par Localisation)
1. Sélectionner le mode "🗺️ Par localisation"
2. Choisir une ville de départ
3. Définir rayon, dates, filtres
4. Visualiser festivals en liste/carte/itinéraire

### Mode Train (Par Itinéraire)
1. Sélectionner le mode "🚂 Par itinéraire train"
2. Indiquer votre ville d'habitation
3. Définir horaires/dates de voyage
4. Sélectionner gare de départ
5. Voir festivals accessibles

---

## 📊 Exemple: Scénario Rennes

**Entrée:**
- Ville: Rennes
- Départ: 18:00 le 02/01/2026
- Retour: 20:00 le 04/01/2026
- Temps max: 6 heures

**Processus:**
1. Trouve 5 gares les plus proches de Rennes
2. Sélectionne la gare (ex: Rennes SNCF)
3. Filtre festivals accessibles en 6h de train
4. Affiche liste + carte + détails

**Sortie:**
- Festivals dans la fenêtre de temps
- Distance en km et temps train estimé
- Localisation sur carte interactive

---

## 🔍 Validation

- ✅ Chargement CSV multi-fichiers
- ✅ Parsing des coordonnées (format "lat, lon")
- ✅ Filtrage par distance (Haversine)
- ✅ Dual-mode UI (radio buttons)
- ✅ Session state Streamlit
- ✅ Cartes Folium interactives
- ✅ Itinéraires optimisés

---

## 📝 Notes

- Les données de festivals n'ont pas de dates spécifiques (mode texte "période")
- Les distances sont calculées via formule Haversine
- Vitesse train estimée: ~100 km/h
- L'application recharge automatiquement lors des changements de paramètres

---

## 🎯 Prochaines Étapes (Optionnel)

1. Intégrer vraies dates depuis colonnes "Période principale"
2. Connecter API SNCF réelle pour horaires de trains
3. Ajouter recherche d'hébergement
4. Exporter itinéraire en PDF
5. Système de favoris/signets

---

**Dernière mise à jour:** 2025-12-30
**Status:** ✅ PRODUCTION READY
