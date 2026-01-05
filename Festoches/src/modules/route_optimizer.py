"""
Module d'optimisation d'itinéraire
"""
import pandas as pd
from typing import List, Dict, Tuple
from haversine import haversine


class RouteOptimizer:
    """Classe pour optimiser les itinéraires entre gares et festivals"""
    
    def __init__(self, stations_df: pd.DataFrame, festivals_df: pd.DataFrame):
        self.stations_df = stations_df
        self.festivals_df = festivals_df
    
    def find_nearest_station(self, latitude: float, longitude: float, num_stations: int = 3) -> pd.DataFrame:
        """
        Trouve les gares les plus proches d'une localisation
        
        Args:
            latitude: latitude du point
            longitude: longitude du point
            num_stations: nombre de gares à retourner
            
        Returns:
            DataFrame avec les gares triées par distance
        """
        result = self.stations_df.copy()
        result['distance'] = result.apply(
            lambda row: haversine(
                (latitude, longitude),
                (row['latitude'], row['longitude']),
                unit='km'
            ),
            axis=1
        )
        return result.nsmallest(num_stations, 'distance')
    
    def calculate_distance_between_festivals(self, festival1: Dict, festival2: Dict) -> float:
        """
        Calcule la distance entre deux festivals
        
        Args:
            festival1: dictionnaire avec latitude et longitude
            festival2: dictionnaire avec latitude et longitude
            
        Returns:
            Distance en km
        """
        return haversine(
            (festival1['latitude'], festival1['longitude']),
            (festival2['latitude'], festival2['longitude']),
            unit='km'
        )
    
    def optimize_tour(self, festivals: List[Dict], start_point: Tuple[float, float] = None) -> List[Dict]:
        """
        Optimise l'ordre de visite des festivals (algorithme glouton)
        
        Args:
            festivals: liste des festivals
            start_point: point de départ (latitude, longitude)
            
        Returns:
            Liste des festivals ordonnée de façon optimisée
        """
        if not festivals:
            return []
        
        if len(festivals) <= 2:
            return festivals
        
        # Convertir en liste de dictionnaires
        festivals_list = [f.to_dict() if hasattr(f, 'to_dict') else f for f in festivals]
        remaining = festivals_list.copy()
        tour = []
        
        # Point de départ
        if start_point:
            current_pos = start_point
        else:
            current_pos = (festivals_list[0]['latitude'], festivals_list[0]['longitude'])
            tour.append(remaining.pop(0))
        
        # Algorithme glouton : ajouter le festival le plus proche
        while remaining:
            nearest_idx = 0
            nearest_distance = float('inf')
            
            for idx, festival in enumerate(remaining):
                dist = haversine(
                    current_pos,
                    (festival['latitude'], festival['longitude']),
                    unit='km'
                )
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_idx = idx
            
            nearest_festival = remaining.pop(nearest_idx)
            tour.append(nearest_festival)
            current_pos = (nearest_festival['latitude'], nearest_festival['longitude'])
        
        return tour
    
    def get_route_summary(self, tour: List[Dict]) -> Dict:
        """
        Génère un résumé de l'itinéraire
        
        Args:
            tour: liste ordonnée des festivals
            
        Returns:
            Dictionnaire avec les statistiques de l'itinéraire
        """
        if not tour or len(tour) < 2:
            return {'total_distance': 0, 'num_festivals': len(tour)}
        
        total_distance = 0
        for i in range(len(tour) - 1):
            dist = haversine(
                (tour[i]['latitude'], tour[i]['longitude']),
                (tour[i+1]['latitude'], tour[i+1]['longitude']),
                unit='km'
            )
            total_distance += dist
        
        return {
            'total_distance': round(total_distance, 2),
            'num_festivals': len(tour),
            'average_distance_between': round(total_distance / (len(tour) - 1), 2) if len(tour) > 1 else 0
        }
