import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from utils.logging_config import logger

# Adjust path to locate the models folder
# Go up from backend/modeling/ to backend/data/models
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_PATH = BASE_DIR / "data/models"

class TrafficPredictor:
    def __init__(self, model_name="xgboost_v1.pkl", preprocessor_name="preprocessor_v1.pkl"):
        """
        Loads the trained model (XGBoost) and preprocessor (Scaler/Encoder).
        """
        self.model_path = MODELS_PATH / model_name
        self.preprocessor_path = MODELS_PATH / preprocessor_name
        
        try:
            self.model = joblib.load(self.model_path)
            self.preprocessor = joblib.load(self.preprocessor_path)
            logger.info(f"Model and Preprocessor loaded from {MODELS_PATH}")
        except Exception as e:
            logger.error(f"Critical error loading model: {e}")
            self.model = None
            self.preprocessor = None

    def predict_batch(self, df_input: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts intensity for a batch of stations (DataFrame).
        
        Args:
            df_input: DataFrame containing all raw features (cols from DB + Lags).
            
        Returns:
            pd.DataFrame: Input DataFrame enriched with 'predicted_intensity' column.
        """
        if not self.model or not self.preprocessor:
            logger.error("Model not loaded. Cannot predict.")
            return None

        try:
            # 1. Transform features (Scaling/Encoding) using the pre-fitted preprocessor
            X_processed, _ = self.preprocessor.transform(df_input)
            
            # 2. Predict
            predictions = self.model.predict(X_processed)
            
            # 3. Format results
            results = np.maximum(0, np.round(predictions)).astype(int)
            
            # Add prediction to DataFrame
            df_result = df_input.copy()
            df_result['predicted_intensity'] = results
            
            return df_result
            
        except Exception as e:
            logger.error(f"Error during batch prediction: {e}")
            return None