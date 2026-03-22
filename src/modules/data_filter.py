"""
Module de filtrage et recherche de festivals
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple


class FestivalFilter:
    """Classe pour filtrer les festivals selon les critères de l'utilisateur"""
    
    def __init__(self, festivals_df: pd.DataFrame):
        self.festivals_df = festivals_df.copy()
    
    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Filtre les festivals par plage de dates
        
        Args:
            start_date: date de début
            end_date: date de fin
            
        Returns:
            DataFrame filtré
        """
        mask = (self.festivals_df['date_debut'] <= end_date) & (self.festivals_df['date_fin'] >= start_date)
        return self.festivals_df[mask]
    
    def filter_by_location(self, latitude: float, longitude: float, radius_km: float = 100) -> pd.DataFrame:
        """
        Filtre les festivals par proximité géographique
        
        Args:
            latitude: latitude du point central
            longitude: longitude du point central
            radius_km: rayon de recherche en km
            
        Returns:
            DataFrame filtré avec colonne 'distance'
        """
        from haversine import haversine
        
        result = self.festivals_df.copy()
        result['distance'] = result.apply(
            lambda row: haversine(
                (latitude, longitude),
                (row['latitude'], row['longitude']),
                unit='km'
            ),
            axis=1
        )
        
        result = result[result['distance'] <= radius_km]
        return result.sort_values('distance')
    
    def filter_combined(self, 
                       start_date: datetime, 
                       end_date: datetime,
                       latitude: float, 
                       longitude: float,
                       radius_km: float = 100) -> pd.DataFrame:
        """
        Filtre les festivals selon plusieurs critères
        
        Args:
            start_date: date de début
            end_date: date de fin
            latitude: latitude du point central
            longitude: longitude du point central
            radius_km: rayon de recherche en km
            
        Returns:
            DataFrame filtré
        """
        # Filtre par date
        filtered = self.filter_by_date_range(start_date, end_date)
        
        # Filtre par localisation
        if len(filtered) > 0:
            from haversine import haversine
            filtered = filtered.copy()
            filtered['distance'] = filtered.apply(
                lambda row: haversine(
                    (latitude, longitude),
                    (row['latitude'], row['longitude']),
                    unit='km'
                ),
                axis=1
            )
            filtered = filtered[filtered['distance'] <= radius_km]
            filtered = filtered.sort_values('distance')
        
        return filtered
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories uniques"""
        if 'categorie' in self.festivals_df.columns:
            return self.festivals_df['categorie'].unique().tolist()
        return []
    
    def filter_by_category(self, category: str) -> pd.DataFrame:
        """
        Filtre les festivals par catégorie
        
        Args:
            category: catégorie du festival
            
        Returns:
            DataFrame filtré
        """
        if 'categorie' in self.festivals_df.columns:
            return self.festivals_df[self.festivals_df['categorie'] == category]
        return self.festivals_df
