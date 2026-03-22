"""
Tests unitaires pour les modules de l'application
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter le répertoire src au chemin
sys.path.insert(0, str(Path(__file__).parent))

from src.modules import FestivalFilter, RouteOptimizer, MapVisualizer


class TestFestivalFilter:
    """Tests du module FestivalFilter"""
    
    @pytest.fixture
    def sample_festivals(self):
        """Crée un DataFrame de festivals d'exemple"""
        return pd.DataFrame({
            'nom': ['Festival A', 'Festival B', 'Festival C'],
            'date_debut': [
                datetime(2024, 6, 1),
                datetime(2024, 7, 1),
                datetime(2024, 8, 1)
            ],
            'date_fin': [
                datetime(2024, 6, 5),
                datetime(2024, 7, 5),
                datetime(2024, 8, 5)
            ],
            'latitude': [48.8566, 45.7640, 43.2965],
            'longitude': [2.3522, 4.8357, 5.3698],
            'categorie': ['Rock', 'Jazz', 'Classique']
        })
    
    def test_filter_by_date_range(self, sample_festivals):
        """Test le filtrage par date"""
        filter_obj = FestivalFilter(sample_festivals)
        
        result = filter_obj.filter_by_date_range(
            datetime(2024, 6, 1),
            datetime(2024, 6, 30)
        )
        
        assert len(result) == 1
        assert result.iloc[0]['nom'] == 'Festival A'
    
    def test_get_categories(self, sample_festivals):
        """Test la récupération des catégories"""
        filter_obj = FestivalFilter(sample_festivals)
        categories = filter_obj.get_categories()
        
        assert len(categories) == 3
        assert 'Rock' in categories
    
    def test_filter_by_category(self, sample_festivals):
        """Test le filtrage par catégorie"""
        filter_obj = FestivalFilter(sample_festivals)
        result = filter_obj.filter_by_category('Jazz')
        
        assert len(result) == 1
        assert result.iloc[0]['nom'] == 'Festival B'


class TestRouteOptimizer:
    """Tests du module RouteOptimizer"""
    
    @pytest.fixture
    def sample_data(self):
        """Crée des données d'exemple"""
        festivals = pd.DataFrame({
            'nom': ['Festival 1', 'Festival 2', 'Festival 3'],
            'latitude': [48.8566, 48.8566, 48.8566],
            'longitude': [2.3522, 3.3522, 4.3522]
        })
        
        stations = pd.DataFrame({
            'nom': ['Gare 1', 'Gare 2'],
            'latitude': [48.8566, 48.8566],
            'longitude': [2.3522, 3.3522]
        })
        
        return festivals, stations
    
    def test_optimize_tour(self, sample_data):
        """Test l'optimisation d'itinéraire"""
        festivals_df, stations_df = sample_data
        optimizer = RouteOptimizer(stations_df, festivals_df)
        
        tour = optimizer.optimize_tour(festivals_df.to_dict('records'))
        
        assert len(tour) == 3
        assert all(fest['nom'] for fest in tour)
    
    def test_get_route_summary(self, sample_data):
        """Test le résumé d'itinéraire"""
        festivals_df, stations_df = sample_data
        optimizer = RouteOptimizer(stations_df, festivals_df)
        
        tour = optimizer.optimize_tour(festivals_df.to_dict('records'))
        summary = optimizer.get_route_summary(tour)
        
        assert 'total_distance' in summary
        assert 'num_festivals' in summary
        assert summary['num_festivals'] == 3


class TestMapVisualizer:
    """Tests du module MapVisualizer"""
    
    @pytest.fixture
    def sample_festivals(self):
        """Crée un DataFrame de festivals d'exemple"""
        return pd.DataFrame({
            'nom': ['Festival A', 'Festival B'],
            'latitude': [48.8566, 45.7640],
            'longitude': [2.3522, 4.8357]
        })
    
    def test_create_festival_map(self, sample_festivals):
        """Test la création d'une carte de festivals"""
        visualizer = MapVisualizer()
        m = visualizer.create_festival_map(sample_festivals)
        
        assert m is not None
        assert hasattr(m, 'location')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
