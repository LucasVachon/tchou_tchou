"""
Module de gestion des itinéraires de trains avec festivals
Calcule les festivals accessibles en train selon les horaires SNCF
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from haversine import haversine


class TrainJourneyPlanner:
    """Planificateur d'itinéraires de trains avec festival finder"""
    
    def __init__(self, stations_df: pd.DataFrame, train_schedules_df: pd.DataFrame, 
                 gare_hours_df: pd.DataFrame, festivals_df: pd.DataFrame):
        """
        Initialise le planificateur
        
        Args:
            stations_df: DataFrame des gares
            train_schedules_df: DataFrame des horaires de trains
            gare_hours_df: DataFrame des horaires d'ouverture des gares
            festivals_df: DataFrame des festivals
        """
        self.stations_df = stations_df
        self.train_schedules_df = train_schedules_df
        self.gare_hours_df = gare_hours_df
        self.festivals_df = festivals_df
    
    def find_nearest_stations(self, latitude: float, longitude: float, num_stations: int = 3) -> pd.DataFrame:
        """
        Trouve les gares les plus proches d'une localisation
        
        Args:
            latitude: latitude du point
            longitude: longitude du point
            num_stations: nombre de gares à retourner
            
        Returns:
            DataFrame avec les gares triées par distance
        """
        try:
            result = self.stations_df.copy()
            
            # Gérer les différentes colonnes possibles pour les coordonnées
            lat_col = None
            lon_col = None
            
            for col in result.columns:
                col_lower = col.lower()
                if 'lat' in col_lower and lat_col is None:
                    lat_col = col
                if 'lon' in col_lower and lon_col is None:
                    lon_col = col
            
            if lat_col is None or lon_col is None:
                return pd.DataFrame()
            
            result['distance'] = result.apply(
                lambda row: haversine(
                    (latitude, longitude),
                    (row[lat_col], row[lon_col]),
                    unit='km'
                ) if pd.notna(row[lat_col]) and pd.notna(row[lon_col]) else float('inf'),
                axis=1
            )
            
            result = result[result['distance'] != float('inf')]
            return result.nsmallest(num_stations, 'distance')
        
        except Exception as e:
            print(f"Erreur dans find_nearest_stations: {e}")
            return pd.DataFrame()
    
    def find_festivals_accessible(self, 
                                 departure_station_name: str,
                                 departure_time: datetime,
                                 return_time: datetime,
                                 max_travel_time_hours: float = 6) -> pd.DataFrame:
        """
        Trouve les festivals accessibles en train depuis une gare
        
        Args:
            departure_station_name: nom de la gare de départ
            departure_time: heure/date de départ (datetime)
            return_time: heure/date de retour maximum (datetime)
            max_travel_time_hours: temps de trajet max en heures
            
        Returns:
            DataFrame des festivals accessibles
        """
        try:
            if self.festivals_df is None or len(self.festivals_df) == 0:
                return pd.DataFrame()
            
            # Filtrer les festivals par date
            festivals = self.festivals_df.copy()
            
            # Vérifier les colonnes de dates
            date_cols = [col for col in festivals.columns if 'date' in col.lower()]
            
            if len(date_cols) < 2:
                # Si pas de colonnes de date, retourner tous les festivals
                accessible = festivals.copy()
            else:
                date_debut_col = date_cols[0]
                date_fin_col = date_cols[1] if len(date_cols) > 1 else date_cols[0]
                
                # Convertir en datetime si nécessaire
                if not pd.api.types.is_datetime64_any_dtype(festivals[date_debut_col]):
                    festivals[date_debut_col] = pd.to_datetime(festivals[date_debut_col], errors='coerce')
                if not pd.api.types.is_datetime64_any_dtype(festivals[date_fin_col]):
                    festivals[date_fin_col] = pd.to_datetime(festivals[date_fin_col], errors='coerce')
                
                # Filtre: festival pendant la période disponible ou chevauchement
                accessible = festivals[
                    (festivals[date_fin_col] >= departure_time) & 
                    (festivals[date_debut_col] <= return_time)
                ].copy()
            
            if len(accessible) == 0:
                return pd.DataFrame()
            
            # Ajouter info: temps de trajet estimé
            lat_col = None
            lon_col = None
            for col in self.stations_df.columns:
                col_lower = col.lower()
                if 'lat' in col_lower and lat_col is None:
                    lat_col = col
                if 'lon' in col_lower and lon_col is None:
                    lon_col = col
            
            if lat_col and lon_col and departure_station_name in self.stations_df.values:
                # Trouver les coordonnées de la gare de départ
                try:
                    dept_row = self.stations_df[self.stations_df.iloc[:, 0] == departure_station_name].iloc[0]
                    dept_lat = dept_row[lat_col]
                    dept_lon = dept_row[lon_col]
                    
                    # Calculer distances aux festivals
                    lat_col_fest = None
                    lon_col_fest = None
                    for col in accessible.columns:
                        col_lower = col.lower()
                        if 'lat' in col_lower and lat_col_fest is None:
                            lat_col_fest = col
                        if 'lon' in col_lower and lon_col_fest is None:
                            lon_col_fest = col
                    
                    if lat_col_fest and lon_col_fest:
                        accessible['distance_km'] = accessible.apply(
                            lambda row: haversine(
                                (dept_lat, dept_lon),
                                (row[lat_col_fest], row[lon_col_fest]),
                                unit='km'
                            ) if pd.notna(row[lat_col_fest]) and pd.notna(row[lon_col_fest]) else None,
                            axis=1
                        )
                        
                        # Filtrer par temps de trajet
                        accessible = accessible[accessible['distance_km'] <= max_travel_time_hours * 100]  # ~100km/h en train
                
                except:
                    pass
            
            return accessible.sort_values('distance_km', ascending=True) if 'distance_km' in accessible.columns else accessible
        
        except Exception as e:
            print(f"Erreur dans find_festivals_accessible: {e}")
            return pd.DataFrame()
    
    def get_journey_summary(self, 
                           departure_station: str,
                           departure_time: datetime,
                           return_time: datetime,
                           festival_name: str) -> Dict:
        """
        Génère un résumé du voyage
        
        Args:
            departure_station: gare de départ
            departure_time: heure de départ
            return_time: heure de retour
            festival_name: nom du festival
            
        Returns:
            Dictionnaire avec les détails du voyage
        """
        return {
            'departure_station': departure_station,
            'departure_time': departure_time,
            'return_time': return_time,
            'total_duration_hours': (return_time - departure_time).total_seconds() / 3600,
            'festival': festival_name
        }
    
    def calculate_travel_feasibility(self,
                                    departure_time: datetime,
                                    return_time: datetime,
                                    departure_station_name: str,
                                    festival: Dict) -> Dict:
        """
        Calcule si un festival est accessible selon les contraintes
        
        Args:
            departure_time: heure de départ
            return_time: heure de retour
            departure_station_name: gare de départ
            festival: dictionnaire avec infos du festival
            
        Returns:
            Dictionnaire avec faisabilité et détails
        """
        try:
            # Vérifier chevauchement avec les dates du festival
            fest_start = festival.get('date_debut')
            fest_end = festival.get('date_fin')
            
            if fest_start and fest_end:
                if not isinstance(fest_start, datetime):
                    fest_start = pd.to_datetime(fest_start)
                if not isinstance(fest_end, datetime):
                    fest_end = pd.to_datetime(fest_end)
                
                # Chevauchement valide ?
                feasible = (fest_end >= departure_time) and (fest_start <= return_time)
            else:
                feasible = True
            
            return {
                'feasible': feasible,
                'festival_name': festival.get('nom', 'N/A'),
                'overlap_days': (min(return_time, fest_end) - max(departure_time, fest_start)).days if feasible else 0,
                'can_arrive_by_departure': festival.get('distance_km', 0) <= 300 if 'distance_km' in festival else True
            }
        
        except Exception as e:
            return {'feasible': False, 'error': str(e)}
