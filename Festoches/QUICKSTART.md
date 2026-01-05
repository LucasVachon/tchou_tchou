# 🚀 DÉMARRAGE RAPIDE

## 3 étapes pour démarrer

### ✅ Étape 1 : Installation (2 minutes)

```powershell
# Ouvrir PowerShell dans le dossier du projet

# Installer les dépendances
pip install -r requirements.txt
```

### ✅ Étape 2 : Préparer les données (1 minute)

Vos fichiers CSV doivent être dans le dossier `data/` :

```
data/
  └─ festivals-global-festivals-pl.csv  (✅ Vous l'avez déjà !)
```

**Fichiers optionnels (à ajouter si disponibles) :**
```
data/
  ├─ festivals-global-festivals-pl.csv
  ├─ gares_francaises.csv          (optionnel)
  └─ horaires_trains.csv           (optionnel)
```

### ✅ Étape 3 : Lancer l'application (1 minute)

```powershell
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur ! 🎉

---

## 📚 Documentation complète

- **README.md** - Guide complet du projet
- **INSTALLATION.md** - Guide d'installation détaillé
- **DATA_FORMAT.md** - Format des données CSV à utiliser
- **config.py** - Paramètres de configuration de l'application

---

## 🎯 Fonctionnalités principales

✅ **Recherche de festivals** par :
  - 📍 Localisation (ville ou coordonnées)
  - 📅 Plage de dates
  - 🎨 Envergure territoriale

✅ **Visualisations** :
  - 📋 Liste des festivals
  - 🗺️ Carte interactive avec marqueurs
  - 🛤️ Itinéraire optimisé
  - 📊 Statistiques

✅ **Optimisation d'itinéraires** :
  - Distance minimale entre festivals
  - Ordre de visite optimal
  - Intégration aux gares

---

## 🔧 Architecture du projet

```
Festoches/
├── app.py                    ← Application principale
├── config.py                 ← Configuration & constantes
├── requirements.txt          ← Dépendances Python
│
├── src/modules/
│   ├── data_loader.py        ← Chargement des CSV
│   ├── data_filter.py        ← Filtrage des festivals
│   ├── route_optimizer.py    ← Optimisation itinéraires
│   └── map_visualizer.py     ← Cartes interactives
│
├── data/                     ← Dossier des données CSV
│   └── festivals-global-festivals-pl.csv
│
├── README.md                 ← Documentation
├── DATA_FORMAT.md           ← Format des données
└── INSTALLATION.md          ← Guide d'installation
```

---

## ⚡ Raccourcis PowerShell utiles

```powershell
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py

# Générer des données d'exemple
python generate_sample_data.py

# Arrêter l'app
# Appuyez sur Ctrl+C
```

---

## 🆘 Problèmes courants

**"Module not found: streamlit"**
→ Exécutez : `pip install -r requirements.txt`

**"No such file or directory: './data/festivals-global-festivals-pl.csv'"**
→ Assurez-vous que le fichier CSV est dans le dossier `data/`

**"Port 8501 already in use"**
→ Exécutez : `streamlit run app.py --server.port 8502`

---

## 📊 Prochaines étapes

1. ✅ L'app fonctionne ? Bravo !
2. 📤 Importez vos données réelles
3. 🎨 Personnalisez les couleurs/thème dans `.streamlit/config.toml`
4. 🚀 Déployez sur le cloud (Streamlit Cloud, Heroku, etc.)

---

**Questions ?** Consultez README.md ou DATA_FORMAT.md

Bon développement ! 🚀
