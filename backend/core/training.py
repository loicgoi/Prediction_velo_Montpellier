import time
from utils.logging_config import logger


def run_model_training():
    """
    Dummy function that simulates a long model training process.
    In the actual project, this function will call the retraining script.
    """
    logger.info("Démarrage de l'entraînement du modèle...")
    time.sleep(5)  # 5-second training simulation
    logger.info("Entraînement du modèle terminé.")
