import uvicorn
from dotenv import load_dotenv
import os
from backend.utils.logging_config import logger

# Loading environment variables
# This is the first thing to do to make DATABASE_URL available everywhere.
logger.info("Chargement des variables d'environnement...")
load_dotenv()

# Importing application modules AFTER load_dotenv
# The order is crucial: we import the modules that depend on .env
from backend.database.database import DatabaseManager


def init_database():
    """
    Initializes the connection to the database and creates the tables if they do not exist.
    """
    logger.info("Initialisation de la base de données...")
    try:
        # DatabaseManager will automatically read the URL from the environment variables.
        db_manager = DatabaseManager()
        db_manager.init_db()
        logger.info(
            "SUCCÈS : Les tables de la base de données ont été vérifiées/créées."
        )
    except Exception as e:
        logger.error(
            f"ERREUR : Échec de l'initialisation de la base de données. Erreur : {e}"
        )
        # You can decide to stop the application if the database is essential.
        raise


if __name__ == "__main__":
    # Initializes the database when the application starts up
    init_database()

    # Start the Uvicorn server, telling it where to find FastAPI's `app` object
    uvicorn.run("backend.api.api:app", host="0.0.0.0", port=8000, reload=True)
