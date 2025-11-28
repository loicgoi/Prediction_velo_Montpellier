from backend.database.database import db_manager


def get_db_session():
    """
    FastAPI dependency for obtaining a database session.
    Handles opening and closing the session for each request.
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
