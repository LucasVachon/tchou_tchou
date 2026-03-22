# Configuration Streamlit pour l'application de découverte de festivals

## Guide d'installation et démarrage

### Installation rapide

1. **Créer un environnement virtuel (optionnel mais recommandé)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

3. **Placer vos données**
```
Créer un dossier 'data' et y placer :
- festivals-global-festivals-pl.csv
```

4. **Lancer l'application**
```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

### Arrêter l'application

Appuyez sur `Ctrl+C` dans le terminal.

### Configuration avancée

Les paramètres Streamlit sont définis dans `.streamlit/config.toml` :
- Thème personnalisé (couleurs, polices)
- Options du client
- Options du logger

### Fichiers de données requis

**festivals-global-festivals-pl.csv** (obligatoire)
- Colonnes: nom, date_debut, date_fin, latitude, longitude, Envergure territoriale

**gares_francaises.csv** (optionnel)
- Colonnes: nom, latitude, longitude

**horaires_trains.csv** (optionnel)
- Colonnes: gare_depart, gare_arrivee, date, heure_depart, heure_arrivee

### Troubleshooting

**Port 8501 déjà utilisé**
```powershell
streamlit run app.py --server.port 8502
```

**Modifier le thème**
Éditez `.streamlit/config.toml` dans la section `[theme]`

---
Pour plus d'informations, consultez le README.md
