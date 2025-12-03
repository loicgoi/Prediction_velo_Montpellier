import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from utils.logging_config import logger

# Chemin vers le dossier de sauvegarde du modèle entrainé et scaler
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_PATH = BASE_DIR / "data/models"

class TrafficPredictor:
    def __init__(self, model_name="xgboost_v1.pkl", preprocessor_name="preprocessor_v1.pkl"):
        """
        Loads the trained model and preprocessor.
        """
        self.model_path = MODELS_PATH / model_name
        self.preprocessor_path = MODELS_PATH / preprocessor_name
        
        try:
            self.model = joblib.load(self.model_path)
            self.preprocessor = joblib.load(self.preprocessor_path)
            logger.info(f"Model and preprocessor loaded from {MODELS_PATH}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.preprocessor = None

    def predict_batch(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts intensity for a DataFrame of stations (J0).
        df_input must contain all raw features (cols from DB + Lags).
        """
        if not self.model or not self.preprocessor:
            logger.error("Model not loaded.")
            return df_input

        try:
            # 1. Transform features (Scaling/Encoding) using the pre-fitted preprocessor
            # We assume df_input has already passed through FeatureEngineering (except lags)
            X_processed, _ = self.preprocessor.transform(df_input)
            
            # 2. Predict
            predictions = self.model.predict(X_processed)
            
            # 3. Add result to dataframe
            # Ensure non-negative predictions
            df_input['predicted_intensity'] = np.maximum(0, np.round(predictions)).astype(int)
            
            return df_input
        except Exception as e:
            logger.error(f"Error during batch prediction: {e}")
            return df_input