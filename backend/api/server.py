import uvicorn
from dotenv import load_dotenv
import os
from utils.logging_config import logger


logger.info("Loading environment variables...")
load_dotenv()

# Importing application modules AFTER load_dotenv
# The order is crucial: we import the modules that depend on .env
from database.database import DatabaseManager


def init_database():
    """
    Initializes the connection to the database and creates the tables if they do not exist.
    """
    logger.info("Initialisation de la base de données...")
    try:
        # DatabaseManager will automatically read the URL from the environment variables.
        db_manager = DatabaseManager()
        db_manager.init_db()
        logger.info("SUCCESS: Database tables have been verified/created.")
    except Exception as e:
        logger.error(f"ERROR: Database initialization failed. Error: {e}")
        # You can decide to stop the application if the database is essential.
        raise


if __name__ == "__main__":
    # Initializes the database when the application starts up
    init_database()

    # Start the Uvicorn server, telling it where to find FastAPI's `app` object
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
