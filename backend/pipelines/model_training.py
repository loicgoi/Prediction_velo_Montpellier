import pandas as pd
from modeling.preprocessor import DataPreprocessor
from modeling.trainer import ModelTrainer
from utils.logging_config import logger

def train_model_pipeline(df: pd.DataFrame):
    """
    Orchestre le pipeline d'entraînement FINAL (Production) :
    1. Préprocessing (Fit & Transform sur TOUT le dataset)
    2. Entraînement (GridSearch sur TOUT le dataset)
    3. Sauvegarde
    """
    logger.info("--- Démarrage de l'Entraînement Final (Production) ---")

    # 0. Vérification & Tri
    if 'date' not in df.columns:
        logger.error("Colonne 'date' manquante.")
        return
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date', 'station_id'])
    
    logger.info(f"Dataset complet : {len(df)} lignes. Le modèle va apprendre sur l'ensemble.")

    # 1. Préprocessing sur l'ensemble des données
    try:
        preprocessor = DataPreprocessor()
        
        preprocessor.fit(df)
        
        # TRANSFORM sur tout le monde
        X, y = preprocessor.transform(df)
        
    except Exception as e:
        logger.error(f"Erreur lors du préprocessing : {e}")
        return

    # 2. Entraînement
    try:
        trainer = ModelTrainer()
        trainer.train(X, y)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement : {e}")
        return

    # 3. Pas d'évaluation "Test Set"
    logger.info("Pas d'évaluation finale (toutes les données ont été utilisées pour l'entraînement).")

    # 4. Sauvegarde
    trainer.save("xgboost_v1.pkl")
    preprocessor.save("preprocessor_v1.pkl")
    
    logger.info("Modèle de production sauvegardé et prêt.")