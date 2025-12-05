import os
from pathlib import Path
from dotenv import load_dotenv
from database.database import DatabaseManager
from utils.logging_config import logger

# We retrieve the path of the current file (backend/core/dependencies.py)
current_file_path = Path(__file__).resolve()

# We go up the tree structure to find the root of the project.
project_root = current_file_path.parent.parent.parent
env_path = project_root / ".env"

# We force loading from this specific path
load_dotenv(dotenv_path=env_path)

# Verification and Instantiation

db_url = os.getenv("DATABASE_URL")

if not db_url:
    logger.warning("ALERT: DATABASE_URL is empty!")
    logger.warning("The API will switch to SQLite (empty database).")
else:
    logger.info("Starting the API with the database!")

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
