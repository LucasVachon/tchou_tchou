# Notebook : Analyse du Chevauchement Festivals-Gares (France Métropolitaine)

## Description

Ce notebook Jupyter offre une visualisation interactive et une analyse détaillée de la répartition des festivals français 2019 en relation avec le réseau ferroviaire SNCF, **limité à la France métropolitaine** (excluant la Corse et les outre-mers).

## Contenu du notebook

### 1. Imports et Configuration
- Pandas, NumPy pour la manipulation de données
- Folium pour les cartes interactives
- Scikit-learn (DBSCAN) pour le clustering
- Matplotlib pour les visualisations statiques

### 2. Chargement des données
- **Festivals** : 7 283 festivals nationaux, 7 051 en France métropolitaine
- **Gares** : 2 785 gares SNCF, 2 778 en France métropolitaine

### 3. Extraction des coordonnées
- Parsing des colonnes "Géocodage xy" (festivals) et "Position géographique" (gares)
- Conversion en latitude/longitude valides

### 4. Filtrage France métropolitaine
- Exclusion des régions non-métropolitaines : Corse, Mayotte, Réunion, Guadeloupe, Martinique, Guyane
- Filtrage géographique : lat 41.3°-51.1°, lon -5.3°-8.3°

### 5. Analyse de distances
- Calcul des distances euclidiques de chaque festival à sa gare la plus proche
- Conversion en kilomètres (1 degré ≈ 111 km)
- Statistiques : moyenne, min, max, médiane

### 6. Clustering DBSCAN
- Identification des groupes de festivals géographiquement proches
- Analyse de la couverture ferroviaire par cluster

### 7. Visualisation cartographique
- Création d'une carte Folium interactive
- **Code couleur des festivals** :
  - 🟢 **Vert** : Bien desservi (< 10 km)
  - 🟠 **Orange** : Correctement desservi (10-30 km)
  - 🔴 **Rouge** : Mal desservi (> 30 km)
- 🔷 **Bleu** : Gares ferroviaires
- Légende complète et popups détaillés

### 8. Graphiques d'analyse
- Scatter plot des festivals avec code couleur
- Boîtes à moustaches montrant la distribution des distances par cluster

### 9. Statistiques par région
- Nombre de festivals par région
- Distance moyenne
- Pourcentage bien/mal desservis

## Sorties générées

### 1. `output_map_chevauchement_metropole.html`
- Carte interactive Folium (13,2 MB)
- Zoommable et navigable
- Clic sur les points pour voir les détails
- Peut être ouverte dans n'importe quel navigateur web

### 2. `output_clusters_analysis.png`
- Deux graphiques côte à côte (718 KB)
- **Gauche** : Visualisation spatiale avec code couleur de couverture
- **Droite** : Distribution des distances par cluster

### 3. Analyse textuelle complète
- Statistiques détaillées en console
- Résumé par région

## Comment exécuter

### Option 1 : Exécuter tout le notebook
```
Ctrl + Shift + Enter (VS Code)
```

### Option 2 : Exécuter cellule par cellule
```
Ctrl + Enter sur chaque cellule
```

### Option 3 : Depuis la ligne de commande
```bash
jupyter nbconvert --to notebook --execute ChevauchementGaresFestivals.ipynb
```

## Résultats clés

- **7 051 festivals** en France métropolitaine
- **2 778 gares** en France métropolitaine
- **75,7%** des festivals à moins de 10 km d'une gare
- **96,7%** des festivals à moins de 30 km d'une gare
- **Distance moyenne** : 7,14 km
- **4 clusters** identifiés + 1 festival isolé

## Meilleures dessertes par région

| Région | Distance moyenne | % bien desservi | Festivals |
|--------|------------------|-----------------|-----------|
| Île-de-France | 1,88 km | 99,5% | 653 |
| Hauts-de-France | 3,45 km | 92,3% | 338 |
| Grand Est | 5,24 km | 83,1% | 467 |

## Zones nécessitant amélioration

| Région | Distance moyenne | % bien desservi | Festivals |
|--------|------------------|-----------------|-----------|
| Occitanie | 9,25 km | 66,8% | 900 |
| Bretagne | 9,56 km | 64,1% | 590 |
| Provence-Alpes-Côte d'Azur | 8,53 km | 69,5% | 930 |

## Dépendances Python

- pandas
- numpy
- folium
- scipy
- scikit-learn
- matplotlib
- warnings (built-in)

Toutes les dépendances sont pré-installées dans l'environnement Jupyter.

## Notes importantes

1. **Géocodage** : Les coordonnées utilisées proviennent du dataset original. Quelques festivals/gares sans coordonnées valides ont été exclus.

2. **Approximation de distance** : La distance est calculée en degrés puis convertie en km. Cette méthode est suffisamment précise pour cette analyse.

3. **Clustering** : Le paramètre DBSCAN `eps=0.3` (≈33 km) crée des clusters représentant des zones géographiques significatives.

4. **Périodes** : Cette analyse porte sur les données de 2019. Les résultats peuvent différer pour d'autres années.

5. **Outre-mers** : Volontairement exclus pour se concentrer sur la France continentale. Un notebook séparé pourrait être créé pour ces régions.

## Améliorations futures

- [ ] Analyse de l'évolution temporelle (2010-2020)
- [ ] Calcul de distance réelle (au lieu d'euclidienne)
- [ ] Analyse de co-localisation (festivals proches vs gares proches)
- [ ] Heatmaps de densité de festivals
- [ ] Analyse socio-économique par région
- [ ] Liens avec les transports routiers complémentaires

---

*Dernier mise à jour : 8 janvier 2026*
