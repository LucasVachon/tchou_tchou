"""
Module de chargement et préparation des données
"""
import pandas as pd
import os
from pathlib import Path


class DataLoader:
    """Classe pour charger et gérer les données"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.festivals_df = None
        self.stations_df = None
        self.schedules_df = None
        self.gare_hours_df = None
        self.train_schedules_df = None
    
    def load_festivals(self, filename: str = "festivals.csv") -> pd.DataFrame:
        """
        Charge les données des festivals
        
        Args:
            filename: nom du fichier CSV
            
        Returns:
            DataFrame avec les festivals
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier {filepath} non trouvé")
        
        self.festivals_df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        self._clean_festivals_data()
        return self.festivals_df
    
    def load_stations(self, filename: str = "gares_francaises.csv") -> pd.DataFrame:
        """
        Charge les données des gares françaises
        
        Args:
            filename: nom du fichier CSV
            
        Returns:
            DataFrame avec les gares
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier {filepath} non trouvé")
        
        self.stations_df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        self._clean_stations_data()
        return self.stations_df
    
    def load_schedules(self, filename: str = "horaires_trains.csv") -> pd.DataFrame:
        """
        Charge les horaires des trains
        
        Args:
            filename: nom du fichier CSV
            
        Returns:
            DataFrame avec les horaires
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier {filepath} non trouvé")
        
        self.schedules_df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        self._clean_schedules_data()
        return self.schedules_df
    
    def load_gare_hours(self, filename: str = "horaires-des-gares1.csv") -> pd.DataFrame:
        """
        Charge les horaires d'ouverture des gares
        
        Args:
            filename: nom du fichier CSV
            
        Returns:
            DataFrame avec les horaires des gares
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier {filepath} non trouvé")
        
        self.gare_hours_df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        return self.gare_hours_df
    
    def load_train_schedules(self, filename: str = "horaires-sncf.csv") -> pd.DataFrame:
        """
        Charge les informations sur les horaires SNCF (liens de téléchargement)
        
        Args:
            filename: nom du fichier CSV
            
        Returns:
            DataFrame avec les informations SNCF
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier {filepath} non trouvé")
        
        self.train_schedules_df = pd.read_csv(filepath, sep=";", encoding="utf-8")
        return self.train_schedules_df
    
    def _clean_festivals_data(self):
        """Nettoyage des données des festivals"""
        if self.festivals_df is not None:
            # Renommer les colonnes pour avoir des noms standard
            rename_map = {
                '\ufeffNom du festival': 'nom',
                'Envergure territoriale': 'Envergure territoriale',
                'Géocodage xy': 'coordonnees',
                'Période principale de déroulement du festival': 'periode'
            }
            
            # Appliquer les renommages si les colonnes existent
            for old_col, new_col in rename_map.items():
                if old_col in self.festivals_df.columns and old_col != new_col:
                    self.festivals_df.rename(columns={old_col: new_col}, inplace=True)
            
            # Parser les coordonnées (format: "lat, lon")
            if 'coordonnees' in self.festivals_df.columns:
                coords = self.festivals_df['coordonnees'].str.split(',', expand=True)
                self.festivals_df['latitude'] = pd.to_numeric(coords[0].str.strip(), errors='coerce')
                self.festivals_df['longitude'] = pd.to_numeric(coords[1].str.strip(), errors='coerce')
                self.festivals_df.drop('coordonnees', axis=1, inplace=True)
            
            # Créer des colonnes date_debut et date_fin à partir de la période (2019)
            self.festivals_df['date_debut'] = self._parse_period_to_dates(
                self.festivals_df['periode'], 'debut'
            )
            self.festivals_df['date_fin'] = self._parse_period_to_dates(
                self.festivals_df['periode'], 'fin'
            )
            
            # Supprimer les doublons
            self.festivals_df.drop_duplicates(subset=['nom'], inplace=True)
            
            # Supprimer les lignes avec données manquantes essentielles
            essential_cols = ['nom', 'latitude', 'longitude']
            self.festivals_df.dropna(subset=essential_cols, inplace=True)
    
    def _clean_stations_data(self):
        """Nettoyage des données des gares"""
        if self.stations_df is not None:
            # Renommer les colonnes pour avoir des noms standard
            rename_map = {
                'Nom': 'nom',
                'Position géographique': 'coordonnees'
            }
            
            for old_col, new_col in rename_map.items():
                if old_col in self.stations_df.columns and old_col != new_col:
                    self.stations_df.rename(columns={old_col: new_col}, inplace=True)
            
            # Parser les coordonnées (format: "lat, lon")
            if 'coordonnees' in self.stations_df.columns:
                coords = self.stations_df['coordonnees'].str.split(',', expand=True)
                self.stations_df['latitude'] = pd.to_numeric(coords[0].str.strip(), errors='coerce')
                self.stations_df['longitude'] = pd.to_numeric(coords[1].str.strip(), errors='coerce')
                self.stations_df.drop('coordonnees', axis=1, inplace=True)
            
            self.stations_df.drop_duplicates(subset=['nom'], inplace=True)
            essential_cols = ['nom', 'latitude', 'longitude']
            self.stations_df.dropna(subset=essential_cols, inplace=True)
    
    def _clean_schedules_data(self):
        """Nettoyage des données des horaires"""
        if self.schedules_df is not None:
            date_cols = [col for col in self.schedules_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            for col in date_cols:
                if col in self.schedules_df.columns:
                    self.schedules_df[col] = pd.to_datetime(self.schedules_df[col], errors='coerce')
            self.schedules_df.drop_duplicates(inplace=True)
    
    def get_festivals(self) -> pd.DataFrame:
        """Retourne les données des festivals"""
        return self.festivals_df
    
    def get_stations(self) -> pd.DataFrame:
        """Retourne les données des gares"""
        return self.stations_df
    
    def get_schedules(self) -> pd.DataFrame:
        """Retourne les données des horaires"""
        return self.schedules_df
    
    def _parse_period_to_dates(self, period_series: pd.Series, date_type: str = 'debut') -> pd.Series:
        """
        Parse la colonne 'période' texte en dates 2019
        
        Args:
            period_series: Series avec les périodes texte
            date_type: 'debut' ou 'fin'
            
        Returns:
            Series avec les dates parsées en 2019
        """
        import re
        from datetime import datetime
        
        month_map = {
            'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'août': 8,
            'septembre': 9, 'octobre': 10, 'ocotbre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
        }
        
        dates = []
        
        for period in period_series:
            if pd.isna(period):
                # Période vide -> utiliser dates par défaut (toute l'année)
                if date_type == 'debut':
                    dates.append(pd.Timestamp('2019-01-01'))
                else:
                    dates.append(pd.Timestamp('2019-12-31'))
                continue
            
            period_lower = str(period).lower().strip()
            
            # Cas 1: Plage de dates (ex: "Avant-saison (1er janvier - 20 juin)")
            if '(' in period_lower and '-' in period_lower:
                # Chercher les mois dans la plage
                mois_found = []
                for month_name in month_map.keys():
                    if month_name in period_lower:
                        mois_found.append((month_name, month_map[month_name]))
                
                if len(mois_found) >= 2:
                    if date_type == 'debut':
                        month = mois_found[0][1]  # Premier mois
                        try:
                            dates.append(pd.Timestamp(f'2019-{month:02d}-01'))
                        except:
                            dates.append(pd.Timestamp('2019-01-01'))
                    else:  # fin
                        month = mois_found[-1][1]  # Dernier mois
                        try:
                            if month == 12:
                                dates.append(pd.Timestamp('2019-12-31'))
                            else:
                                next_month = pd.Timestamp(f'2019-{month+1:02d}-01')
                                last_day = (next_month - pd.Timedelta(days=1)).day
                                dates.append(pd.Timestamp(f'2019-{month:02d}-{last_day:02d}'))
                        except:
                            dates.append(pd.Timestamp('2019-12-31'))
                else:
                    if date_type == 'debut':
                        dates.append(pd.Timestamp('2019-01-01'))
                    else:
                        dates.append(pd.Timestamp('2019-12-31'))
            
            # Cas 2: Mois unique (ex: "Juin", "Mai")
            else:
                # Chercher le mois
                found_month = None
                for month_name, month_num in month_map.items():
                    if month_name in period_lower:
                        found_month = month_num
                        break
                
                if found_month:
                    if date_type == 'debut':
                        dates.append(pd.Timestamp(f'2019-{found_month:02d}-01'))
                    else:  # fin
                        # Dernier jour du mois
                        if found_month == 12:
                            dates.append(pd.Timestamp('2019-12-31'))
                        else:
                            next_month = pd.Timestamp(f'2019-{found_month+1:02d}-01')
                            last_day = (next_month - pd.Timedelta(days=1)).day
                            dates.append(pd.Timestamp(f'2019-{found_month:02d}-{last_day:02d}'))
                else:
                    # Pas de mois trouvé -> dates par défaut
                    if date_type == 'debut':
                        dates.append(pd.Timestamp('2019-01-01'))
                    else:
                        dates.append(pd.Timestamp('2019-12-31'))
        
        return pd.Series(dates, index=period_series.index)
    
    def get_gare_hours(self) -> pd.DataFrame:
        """Retourne les données des horaires des gares"""
        return self.gare_hours_df
    
    def get_train_schedules(self) -> pd.DataFrame:
        """Retourne les données des informations SNCF"""
        return self.train_schedules_df
