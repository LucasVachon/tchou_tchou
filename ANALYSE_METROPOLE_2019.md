# Analyse des Festivals 2019 - France Métropolitaine

## Résumé exécutif

Cette analyse visualise la répartition des **7 051 festivals français de 2019** en France métropolitaine et leur couverture par le réseau ferroviaire SNCF composé de **2 778 gares**.

### Résultats clés

- **75,7%** des festivals sont à moins de **10 km** d'une gare ferroviaire
- **96,7%** des festivals sont à moins de **30 km** d'une gare ferroviaire
- **Distance moyenne** à la gare la plus proche : **7,14 km**
- **Distance médiane** : **2,99 km**

## Analyse par couverture ferroviaire

### Catégories identifiées

1. **Bien desservis** (< 10 km) : 5 340 festivals (75,7%)
   - Excellente accessibilité par le réseau ferroviaire
   - Plus facile pour les visiteurs d'accéder par train

2. **Correctement desservis** (10-30 km) : 1 476 festivals (21,0%)
   - Accessibilité modérée
   - Nécessite transport complémentaire

3. **Mal desservis** (> 30 km) : 235 festivals (3,3%)
   - Accessibilité faible
   - Dépendant des transports routiers

## Clustering géographique

L'analyse DBSCAN a identifié **4 clusters** de festivals et **1 festival isolé**:

### Cluster 0 (Principal)
- **7 023 festivals** (99,6% du total)
- Distance moyenne à la gare : **7,11 km**
- Bien desservies : 75,8%
- Couvre presque toute la France métropolitaine

### Cluster 1
- **13 festivals** (petit cluster localisé)
- Distance moyenne : **11,60 km**
- Bien desservies : 53,8%

### Cluster 2
- **11 festivals** (petit cluster de bonne couverture)
- Distance moyenne : **6,61 km**
- Bien desservies : 72,7%

### Cluster 3
- **3 festivals** (très éloignés)
- Distance moyenne : **67,79 km**
- Bien desservies : 0%

### Festival isolé
- **1 festival** mal desservi
- Distance : **41,35 km**

## Analyse par région

### Meilleures dessertes

1. **Île-de-France** ⭐⭐⭐
   - Distance moyenne : **1,88 km**
   - Bien desservies : **99,5%** (650/653)
   - 653 festivals

2. **Hauts-de-France** ⭐⭐⭐
   - Distance moyenne : **3,45 km**
   - Bien desservies : **92,3%** (312/338)
   - 338 festivals

3. **Grand Est** ⭐⭐⭐
   - Distance moyenne : **5,24 km**
   - Bien desservies : **83,1%** (388/467)
   - 467 festivals

### Dessertes moyennes

- **Normandie** : 6,52 km moyenne, 74,2% bien desservies
- **Centre-Val de Loire** : 7,37 km moyenne, 74,8% bien desservies
- **Bourgogne-Franche-Comté** : 7,38 km moyenne, 73,8% bien desservies
- **Pays de la Loire** : 7,48 km moyenne, 76,8% bien desservies
- **Nouvelle-Aquitaine** : 7,14 km moyenne, 76,0% bien desservies (828 festivals)

### Dessertes à améliorer

- **Occitanie** : 9,25 km moyenne, 66,8% bien desservies (900 festivals)
- **Bretagne** : 9,56 km moyenne, 64,1% bien desservies (590 festivals)
- **Provence-Alpes-Côte d'Azur** : 8,53 km moyenne, 69,5% bien desservies (930 festivals)
- **Auvergne-Rhône-Alpes** : 8,02 km moyenne, 72,9% bien desservies (947 festivals)

## Observations géographiques

### Zones fortement desservies
- **Île-de-France** : Réseau très dense, presque tous les festivals à proximité immédiate
- **Nord-Pas-de-Calais** : Excellente couverture
- **Région Parisienne et couronne métropolitaine** : Très bien équipées

### Zones avec meilleure couverture relative
- **Auvergne-Rhône-Alpes** : Bonne couverture malgré la grande surface
- **Occitanie** : Régions urbaines bien desservies, zones rurales moins
- **Nouvelle-Aquitaine** : Couverture satisfaisante

### Festivals éloignés
- Principalement dans les zones montagneuses ou rurales isolées
- Auvergne-Rhône-Alpes, Occitanie et Provence-Alpes-Côte d'Azur contiennent les plus de festivals mal desservis

## Fichiers générés

1. **output_map_chevauchement_metropole.html** (13,2 MB)
   - Carte interactive Folium
   - Tous les festivals en métropole
   - Code couleur : vert (bien), orange (moyen), rouge (mal)
   - Tous les pointeurs de gares
   - Légende interactive

2. **output_clusters_analysis.png** (718 KB)
   - Visualisation spatiale des clusters
   - Boîtes à moustaches par cluster
   - Analyse comparative de couverture

3. **ANALYSE_METROPOLE_2019.md** (ce fichier)
   - Résumé complet de l'analyse

## Conclusions

- La France métropolitaine a une **très bonne couverture globale** avec 96,7% des festivals à moins de 30 km d'une gare
- Le réseau ferroviaire est bien adapté pour les **grands festivals** et ceux en zones urbaines
- Les **petits festivals ruraux** ont une accessibilité réduite
- **Île-de-France et le Nord** sont les mieux desservis
- **Occitanie et Bretagne** pourraient bénéficier d'améliorations d'accessibilité

## Méthodologie

- **Filtrage** : Exclusion de la Corse et des outre-mers (régions non-métropolitaines)
- **Géocodage** : Utilisation des coordonnées lat/lon fournies
- **Distances** : Calcul euclidien (1 degré ≈ 111 km)
- **Clustering** : DBSCAN avec eps=0.3 degrés (≈33 km), min_samples=3

---

*Analyse générée le 8 janvier 2026*
*Données : Festivals 2019 et Gares de voyageurs SNCF*
