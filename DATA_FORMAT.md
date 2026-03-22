# 📊 Guide des structures de données

## Format attendu des fichiers CSV

### 1. festivals-global-festivals-pl.csv

**Colonnes requises :**

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `nom` | string | Nom du festival | "Rock en Seine" |
| `date_debut` | date | Date de début (YYYY-MM-DD) | "2024-06-15" |
| `date_fin` | date | Date de fin (YYYY-MM-DD) | "2024-06-17" |
| `latitude` | float | Latitude du lieu | 48.8566 |
| `longitude` | float | Longitude du lieu | 2.3522 |
| `Envergure territoriale` | string | Portée du festival | "National" |

**Colonnes optionnelles :**

| Colonne | Type | Description |
|---------|------|-------------|
| `ville` | string | Ville où se tient le festival |
| `genre` | string | Genre musical principal |
| `capacite` | integer | Capacité d'accueil |
| `url` | string | Site web officiel |
| `description` | string | Description du festival |
| `site_web` | string | URL du site |

**Exemple complet :**
```csv
nom;date_debut;date_fin;latitude;longitude;Envergure territoriale;ville;genre;capacite
Rock en Seine;2024-06-15;2024-06-17;48.8566;2.3522;National;Paris;Rock;80000
Festival d'Aix-en-Provence;2024-07-01;2024-08-31;43.5297;5.4474;International;Aix-en-Provence;Classique;3000
```

### 2. gares_francaises.csv

**Colonnes requises :**

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `nom` | string | Nom de la gare | "Paris-Gare de Lyon" |
| `latitude` | float | Latitude de la gare | 48.8439 |
| `longitude` | float | Longitude de la gare | 2.3738 |

**Colonnes optionnelles :**

| Colonne | Type | Description |
|---------|------|-------------|
| `ville` | string | Ville où se trouve la gare |
| `code_gare` | string | Code SNCF unique |
| `accessible_pmr` | boolean | Accessibilité PMR |
| `type_gare` | string | Type de gare (TGV, régionale, etc.) |

**Exemple :**
```csv
nom;latitude;longitude;ville;code_gare
Paris-Gare de Lyon;48.8439;2.3738;Paris;FRPLY
Gare Montparnasse;48.8349;2.3252;Paris;FRPTM
Gare de Marseille-Saint-Charles;43.3033;5.3611;Marseille;FRMSC
```

### 3. horaires_trains.csv

**Colonnes requises :**

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `gare_depart` | string | Gare de départ | "Paris-Gare de Lyon" |
| `gare_arrivee` | string | Gare d'arrivée | "Gare de Lyon-Perrache" |
| `date` | date | Date du trajet (YYYY-MM-DD) | "2024-06-15" |
| `heure_depart` | time | Heure de départ (HH:MM:SS) | "09:00:00" |
| `heure_arrivee` | time | Heure d'arrivée (HH:MM:SS) | "12:00:00" |

**Colonnes optionnelles :**

| Colonne | Type | Description |
|---------|------|-------------|
| `num_train` | string | Numéro du train |
| `type_train` | string | Type (TGV, TER, etc.) |
| `places_disponibles` | integer | Nombre de places |
| `prix_base` | float | Prix en euros |
| `duree_minutes` | integer | Durée du trajet |

**Exemple :**
```csv
gare_depart;gare_arrivee;date;heure_depart;heure_arrivee;num_train;type_train
Paris-Gare de Lyon;Gare de Lyon-Perrache;2024-06-15;09:00:00;12:00:00;TGV123;TGV
Gare de Lyon-Perrache;Gare Saint-Jean Bordeaux;2024-06-15;14:30:00;18:45:00;TGV125;TGV
```

## 🔍 Validation des données

### Points importants

1. **Séparateur** : Tous les fichiers utilisent `;` comme séparateur (pas `,`)
2. **Encodage** : UTF-8 recommandé pour les caractères français
3. **Dates** : Format YYYY-MM-DD (ISO 8601)
4. **Heures** : Format HH:MM:SS (24h)
5. **Coordonnées** : WGS84 (latitude/longitude standard GPS)

### Contrôle de qualité

**Vérifier les données :**

```python
import pandas as pd

# Charger et vérifier
df = pd.read_csv("data/festivals.csv", sep=";", encoding="utf-8")

# Vérifier les colonnes manquantes
required = ['nom', 'date_debut', 'date_fin', 'latitude', 'longitude']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"Colonnes manquantes : {missing}")

# Vérifier les valeurs nulles
print(df.isnull().sum())

# Vérifier les types
print(df.dtypes)

# Statistiques
print(df.describe())
```

## 📥 Importer des données réelles

### Sources recommandées

1. **Festivals**
   - Atout France: https://www.atout-france.fr/
   - OpenFeast: API événements

2. **Gares SNCF**
   - SNCF DATA: https://data.sncf.com/
   - API Gares & Connexions

3. **Horaires de trains**
   - SNCF Connect API
   - Base GTFS France

### Exemple de transformation

```python
# Si vous avez une source différente
original_df = pd.read_csv("source.csv", sep=",")

# Renommer les colonnes
renamed_df = original_df.rename(columns={
    'festival_name': 'nom',
    'start_date': 'date_debut',
    'end_date': 'date_fin',
    'lat': 'latitude',
    'lon': 'longitude'
})

# Convertir les dates
renamed_df['date_debut'] = pd.to_datetime(renamed_df['date_debut']).dt.strftime('%Y-%m-%d')
renamed_df['date_fin'] = pd.to_datetime(renamed_df['date_fin']).dt.strftime('%Y-%m-%d')

# Sauvegarder
renamed_df.to_csv("data/festivals.csv", sep=";", index=False, encoding="utf-8")
```

## ⚠️ Erreurs communes

1. **Séparateur incohérent** : Mélange `,` et `;`
   → Vérifiez avec un éditeur de texte

2. **Dates invalides** : Format incorrect ou dates impossibles
   → Utilisez `pd.to_datetime()` avec `errors='coerce'`

3. **Coordonnées hors limites** : Lat: -90 à 90, Lon: -180 à 180
   → Vérifiez les valeurs

4. **Doublons** : Mêmes festivals plusieurs fois
   → Utilisez `df.drop_duplicates()`

5. **Valeurs manquantes** : NaN dans les colonnes requises
   → Utilisez `df.dropna(subset=[...])`

## 📝 Script de nettoyage

```python
import pandas as pd

def nettoyer_festivals(filepath):
    """Nettoie et valide un fichier de festivals"""
    df = pd.read_csv(filepath, sep=";", encoding="utf-8")
    
    # Supprimer les doublons
    df = df.drop_duplicates(subset=['nom', 'date_debut', 'date_fin'])
    
    # Convertir les dates
    df['date_debut'] = pd.to_datetime(df['date_debut'], errors='coerce')
    df['date_fin'] = pd.to_datetime(df['date_fin'], errors='coerce')
    
    # Vérifier les coordonnées
    df = df[(df['latitude'] >= -90) & (df['latitude'] <= 90)]
    df = df[(df['longitude'] >= -180) & (df['longitude'] <= 180)]
    
    # Supprimer les données incomplètes
    df = df.dropna(subset=['nom', 'date_debut', 'date_fin', 'latitude', 'longitude'])
    
    return df
```

---

Pour toute question sur le format, consultez le README.md principal.
