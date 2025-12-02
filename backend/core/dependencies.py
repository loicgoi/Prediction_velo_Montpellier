from dotenv import load_dotenv
from database.database import DatabaseManager

load_dotenv()

# Creates a SINGLE instance of DatabaseManager that will be used by the ENTIRE application.
db_manager = DatabaseManager()


def get_db_session():
    """
    FastAPI dependency for obtaining a database session.
    This function will be overridden during tests.
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
