import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from backend.utils.logging_config import logger  
from backend.utils.paths import MODELS_PATH

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.station_encoder = LabelEncoder()
        
        # Liste des features
        self.features_cols = [
            'station_id', 'latitude', 'longitude', 
            'avg_temp', 'precipitation_mm', 'vent_max',
            'day_of_week', 'day_of_year', 'month', 'year',
            'is_weekend',
            'day_of_week_sin', 'day_of_week_cos', 
            'month_sin', 'month_cos', 
            'is_rainy', 'is_cold', 'is_hot', 'is_windy', 
            'lag_1', 'lag_7'
        ]
        self.target_col = 'intensity'

    def fit(self, df):
        """Apprend les paramètres de transformation."""
        logger.info("Préprocessing : Apprentissage des paramètres (Fit)...")
        try:
            
            self.station_encoder.fit(df['station_id'])
            
            cols_to_scale = ['latitude', 'longitude', 'avg_temp', 'precipitation_mm', 'vent_max', 'lag_1', 'lag_7']
            self.scaler.fit(df[cols_to_scale])
            return self
        except Exception as e:
            logger.error(f"Erreur lors du fit du préprocesseur : {e}")
            raise

    def transform(self, df):
        """Applique les transformations."""
        try:
            df_out = df.copy()
            
            # Encodage ID
            df_out['station_id'] = self.station_encoder.transform(df_out['station_id'])
            
            # Scaling
            cols_to_scale = ['latitude', 'longitude', 'avg_temp', 'precipitation_mm', 'vent_max', 'lag_1', 'lag_7']
            df_out[cols_to_scale] = self.scaler.transform(df_out[cols_to_scale])
            
            X = df_out[self.features_cols]
            
            y = None
            if self.target_col in df_out.columns:
                y = df_out[self.target_col]
                
            return X, y
        except Exception as e:
            logger.error(f"Erreur lors de la transformation des données : {e}")
            raise

    def save(self, filename="preprocessor.pkl"):
            """
            Sauvegarde le préprocesseur.
            Si 'filename' est un nom simple, utilise MODELS_PATH.
            """
            try:
                path_obj = Path(filename)
                
                # Si le chemin n'a pas de dossier parent (ex: "preprocessor.pkl")
                if len(path_obj.parts) == 1:
                    target_path = MODELS_PATH / filename
                else:
                    target_path = path_obj

                # Création du dossier parent si besoin (sécurité)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                joblib.dump(self, target_path)
                logger.info(f"Préprocesseur sauvegardé sous : {target_path}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du préprocesseur : {e}")

    @staticmethod
    def load(filename="preprocessor.pkl"):
        """Charge le préprocesseur depuis MODELS_PATH."""
        path_obj = Path(filename)
        if len(path_obj.parts) == 1:
            target_path = MODELS_PATH / filename
        else:
            target_path = path_obj
            
        logger.info(f"Chargement du préprocesseur : {target_path}")
        return joblib.load(target_path)