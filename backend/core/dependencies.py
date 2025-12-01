from backend.database.database import DatabaseManager

# Creates a single instance of the DatabaseManager for the production application.
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
