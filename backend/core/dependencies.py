import os
from pathlib import Path
from dotenv import load_dotenv
from database.database import DatabaseManager
from utils.logging_config import logger

# --- 1. Chargement intelligent du .env ---

# On récupère le chemin du fichier actuel (backend/core/dependencies.py)
current_file_path = Path(__file__).resolve()

# On remonte l'arborescence pour trouver la racine du projet
# dependencies.py -> core -> backend -> Prediction_velo_Montpellier (Racine)
project_root = current_file_path.parent.parent.parent
env_path = project_root / ".env"

# On force le chargement depuis ce chemin spécifique
load_dotenv(dotenv_path=env_path)

# --- 2. Vérification et Instanciation ---

db_url = os.getenv("DATABASE_URL")

if not db_url:
    # Message d'erreur explicite avec le chemin testé
    logger.warning(f"⚠️  ALERTE : DATABASE_URL vide ! (J'ai cherché ici : {env_path})")
    logger.warning("L'API va basculer sur SQLite (base vide).")
else:
    # Masquage du mot de passe pour les logs
    safe_host = db_url.split("@")[-1] if "@" in db_url else "URL non standard"
    logger.info(f"✅  Démarrage API avec la base : {safe_host}")

# On passe l'URL explicite au manager
db_manager = DatabaseManager(database_url=db_url)


def get_db_session():
    """
    FastAPI dependency for obtaining a database session.
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
