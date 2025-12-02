from dotenv import load_dotenv
from database.database import DatabaseManager

# --- MODIFICATION ---
# Charger les variables d'environnement ICI, une seule fois, avant toute chose.
load_dotenv()

# Crée une instance UNIQUE de DatabaseManager qui sera utilisée par TOUTE l'application.
db_manager = DatabaseManager()


def get_db_session():
    """
    FastAPI dependency for obtaining a database session.
    This function will be overridden during tests.
    """
    session = db_manager.get_session()  # Utilise l'instance unique
    try:
        yield session
    finally:
        session.close()
