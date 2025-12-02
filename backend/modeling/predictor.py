import joblib
import pandas as pd
from backend.utils.logging_config import logger 

class TrafficPredictor:
    def __init__(self, model_path, preprocessor_path):
        """Charge le modèle et le préprocesseur."""
        try:
            self.model = joblib.load(model_path)
            self.preprocessor = joblib.load(preprocessor_path)
            logger.info("Modèle et Préprocesseur chargés avec succès.")
        except Exception as e:
            logger.error(f"Erreur critique lors du chargement du modèle : {e}")
            self.model = None
            self.preprocessor = None

    def predict_single(self, input_data):
        """Prévision pour une entrée unique."""
        if not self.model or not self.preprocessor:
            logger.error("Impossible de prédire : Modèle non chargé.")
            return None
            
        try:
            # Conversion en DataFrame
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            else:
                df = input_data
            
            # Transformation
            X_processed, _ = self.preprocessor.transform(df)
            
            # Prédiction
            prediction = self.model.predict(X_processed)
            result = int(prediction[0])
            
            logger.info(f"Prédiction générée : {result} vélos.")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction : {e}")
            return None