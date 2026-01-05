"""
Module de visualisation des données sur carte
"""
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


class MapVisualizer:
    """Classe pour créer des visualisations cartographiques"""
    
    @staticmethod
    def create_festival_map(festivals_df: pd.DataFrame, center_lat: float = 46.5, center_lon: float = 2.2, zoom_start: int = 6) -> folium.Map:
        """
        Crée une carte avec les festivals
        
        Args:
            festivals_df: DataFrame avec les festivals
            center_lat: latitude du centre
            center_lon: longitude du centre
            zoom_start: niveau de zoom initial
            
        Returns:
            Objet folium.Map
        """
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles="OpenStreetMap"
        )
        
        # Ajouter les festivals
        for idx, row in festivals_df.iterrows():
            popup_text = f"""
            <b>{row.get('nom', 'Festival')}</b><br>
            Distance: {row.get('distance', row.get('distance_km', 'N/A'))} km<br>
            Discipline: {row.get('Discipline dominante', 'N/A')}
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=row.get('nom', 'Festival'),
                icon=folium.Icon(color='red', icon='music')
            ).add_to(m)
        
        return m
    
    @staticmethod
    def create_stations_map(stations_df: pd.DataFrame, center_lat: float = 46.5, center_lon: float = 2.2, zoom_start: int = 6) -> folium.Map:
        """
        Crée une carte avec les gares
        
        Args:
            stations_df: DataFrame avec les gares
            center_lat: latitude du centre
            center_lon: longitude du centre
            zoom_start: niveau de zoom initial
            
        Returns:
            Objet folium.Map
        """
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles="OpenStreetMap"
        )
        
        # Ajouter les gares
        for idx, row in stations_df.iterrows():
            popup_text = f"""
            <b>{row.get('nom', 'Gare')}</b><br>
            Distance: {row.get('distance', 'N/A')} km
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=row.get('nom', 'Gare'),
                icon=folium.Icon(color='blue', icon='train')
            ).add_to(m)
        
        return m
    
    @staticmethod
    def create_itinerary_map(festivals_df: pd.DataFrame, stations_df: pd.DataFrame = None, 
                            center_lat: float = 46.5, center_lon: float = 2.2, zoom_start: int = 6) -> folium.Map:
        """
        Crée une carte avec festivals et gares et les connexions
        
        Args:
            festivals_df: DataFrame avec les festivals
            stations_df: DataFrame avec les gares
            center_lat: latitude du centre
            center_lon: longitude du centre
            zoom_start: niveau de zoom initial
            
        Returns:
            Objet folium.Map
        """
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles="OpenStreetMap"
        )
        
        # Ajouter les gares
        if stations_df is not None and len(stations_df) > 0:
            for idx, row in stations_df.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"<b>{row.get('nom', 'Gare')}</b>",
                    icon=folium.Icon(color='blue', icon='train')
                ).add_to(m)
        
        # Ajouter les festivals et les relier
        coords = []
        for idx, row in festivals_df.iterrows():
            popup_text = f"<b>{row.get('nom', 'Festival')}</b>"
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup_text,
                icon=folium.Icon(color='red', icon='music')
            ).add_to(m)
            coords.append([row['latitude'], row['longitude']])
        
        # Tracer les connexions entre festivals
        if len(coords) > 1:
            folium.PolyLine(
                coords,
                color='red',
                weight=2,
                opacity=0.7,
                popup='Itinéraire'
            ).add_to(m)
        
        return m
