#!/usr/bin/env python
"""
Script de vérification de l'installation
Teste que tout est correctement configuré pour lancer l'application
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    print("[PYTHON] Verification de la version Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   OK Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ERREUR Python {version.major}.{version.minor} (au minimum 3.8 requis)")
        return False

def check_packages():
    """Vérifie que tous les packages requis sont installés"""
    print("\n[PACKAGES] Verification des packages Python...")
    
    required_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('plotly', 'plotly'),
        ('folium', 'folium'),
        ('streamlit-folium', 'streamlit_folium'),
        ('haversine', 'haversine'),
        ('scikit-learn', 'sklearn')
    ]
    
    all_ok = True
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"   OK {package_name}")
        except ImportError:
            print(f"   ERREUR {package_name} (manquant)")
            all_ok = False
    
    return all_ok

def check_data_files():
    """Vérifie que les fichiers de données existent"""
    print("\n📁 Vérification des fichiers de données...")
    
    data_dir = Path("./data")
    
    if not data_dir.exists():
        print(f"   ⚠️  Dossier './data' n'existe pas")
        print(f"   → Création du dossier...")
        data_dir.mkdir(exist_ok=True)
        print(f"   ✅ Dossier créé")
    else:
        print(f"   ✅ Dossier './data' existe")
    
    # Vérifier les fichiers
    required_file = "festivals-global-festivals-pl.csv"
    festivals_file = data_dir / required_file
    
    if festivals_file.exists():
        print(f"   ✅ {required_file} trouvé")
        return True
    else:
        print(f"   ⚠️  {required_file} non trouvé")
        print(f"   → L'application fonctionnera mais sans données")
        return False

def check_project_structure():
    """Vérifie la structure du projet"""
    print("\n📂 Vérification de la structure du projet...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'config.py'
    ]
    
    required_dirs = [
        'src',
        'src/modules',
        '.streamlit'
    ]
    
    all_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} manquant")
            all_ok = False
    
    for dir in required_dirs:
        if Path(dir).exists():
            print(f"   ✅ {dir}/")
        else:
            print(f"   ❌ {dir}/ manquant")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale"""
    print("=" * 50)
    print("[INFO] VERIFICATION DE L'INSTALLATION")
    print("=" * 50)
    
    results = {
        'Python': check_python_version(),
        'Packages': check_packages(),
        'Structure': check_project_structure(),
        'Données': check_data_files()
    }
    
    print("\n" + "=" * 50)
    print("[RESUME]")
    print("=" * 50)
    
    for check, result in results.items():
        status = "OK" if result else "ERREUR"
        print(f"{check}: {status}")
    
    print("\n" + "=" * 50)
    
    if all(results.values()):
        print("🎉 Tout est prêt ! Vous pouvez lancer :")
        print("   streamlit run app.py")
    elif results['Python'] and results['Packages'] and results['Structure']:
        print("⚠️  Il manque les données CSV, mais l'app peut tourner.")
        print("   Lancez : streamlit run app.py")
        print("\n   Pour ajouter des données :")
        print("   1. Mettez festivals-global-festivals-pl.csv dans ./data/")
        print("   2. Relancez l'application")
    else:
        print("❌ Veuillez corriger les erreurs ci-dessus")
        print("\n💡 Pour installer les packages manquants :")
        print("   pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
