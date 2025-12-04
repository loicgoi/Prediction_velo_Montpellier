import sys
import os
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# --- CONFIGURATION DES CHEMINS ---
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from backend.modeling.preprocessor import DataPreprocessor
from backend.modeling.trainer import ModelTrainer

# --- FIXTURES (Données de préparation) ---

@pytest.fixture
def mock_data():
    """Génère un dataset factice pour les tests."""
    n_rows = 50
    dates = pd.date_range(start='2024-01-01', periods=n_rows, freq='D')
    
    data = {
        'date': dates,
        'station_id': np.random.choice(['Station_A', 'Station_B'], n_rows),
        'latitude': np.random.uniform(43.5, 43.7, n_rows),
        'longitude': np.random.uniform(3.8, 4.0, n_rows),
        'avg_temp': np.random.uniform(0, 35, n_rows),
        'precipitation_mm': np.random.uniform(0, 10, n_rows),
        'vent_max': np.random.uniform(0, 50, n_rows),
        'intensity': np.random.randint(0, 1000, n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # Feature Engineering minimal simulé
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_holiday'] = 0
    df['day_of_week_sin'] = 0.5
    df['day_of_week_cos'] = 0.5
    df['month_sin'] = 0.5
    df['month_cos'] = 0.5
    df['is_rainy'] = 0
    df['is_cold'] = 0
    df['is_hot'] = 0
    df['is_windy'] = 0
    df['lag_1'] = df['intensity'].shift(1).fillna(0)
    df['lag_7'] = df['intensity'].shift(7).fillna(0)
    
    return df

@pytest.fixture
def processed_data(mock_data):
    """Retourne X et y déjà transformés par le préprocesseur."""
    processor = DataPreprocessor()
    return processor.fit(mock_data).transform(mock_data)

# --- TESTS ---

def test_preprocessor_fit_transform(mock_data):
    """Vérifie que le préprocesseur transforme bien les données."""
    processor = DataPreprocessor()
    
    # Test du Fit
    processor.fit(mock_data)
    # On vérifie que l'encodeur a bien appris les classes (Station_A, Station_B)
    assert len(processor.station_encoder.classes_) > 0
    
    # Test du Transform
    X, y = processor.transform(mock_data)
    
    # Vérifications
    assert X is not None
    assert y is not None
    assert len(X) == len(mock_data)
    assert len(y) == len(mock_data)
    # Vérifie qu'on a bien toutes les colonnes attendues (22 features définies dans la classe)
    assert X.shape[1] == len(processor.features_cols)

def test_preprocessor_save_load(mock_data, tmp_path):
    """Vérifie la sauvegarde et le chargement du préprocesseur."""
    # tmp_path est une fixture magique de Pytest qui crée un dossier temporaire
    save_path = tmp_path / "test_preprocessor.pkl"
    
    processor = DataPreprocessor()
    processor.fit(mock_data)
    
    # Sauvegarde
    processor.save(save_path)
    assert save_path.exists()
    
    # Chargement
    loaded_processor = DataPreprocessor.load(save_path)
    assert loaded_processor is not None
    # On vérifie qu'il a gardé sa mémoire (le scaler)
    assert hasattr(loaded_processor, 'scaler')

def test_trainer_execution(processed_data):
    """Vérifie que l'entraînement tourne sans planter."""
    X, y = processed_data
    trainer = ModelTrainer()
    
    # On réduit le nombre d'estimateurs pour que le test soit instantané
    trainer.model.set_params(n_estimators=2)
    
    # Lancement de l'entraînement
    trainer.train(X, y)
    
    assert trainer.best_model is not None

def test_trainer_evaluation(processed_data):
    """Vérifie que l'évaluation renvoie bien un score RMSE."""
    X, y = processed_data
    trainer = ModelTrainer()
    trainer.model.set_params(n_estimators=2)
    trainer.train(X, y)
    
    rmse = trainer.evaluate(X, y)
    
    assert isinstance(rmse, float)
    assert rmse >= 0

def test_trainer_save(processed_data, tmp_path):
    """Vérifie la sauvegarde du modèle."""
    X, y = processed_data
    save_path = tmp_path / "test_model.pkl"
    
    trainer = ModelTrainer()
    trainer.model.set_params(n_estimators=2)
    trainer.train(X, y)
    
    trainer.save(save_path)
    assert save_path.exists()