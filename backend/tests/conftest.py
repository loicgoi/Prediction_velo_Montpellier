import pytest
from sqlalchemy.orm import Session
from typing import Generator

from backend.database.database import DatabaseManager

# Utilise une base de données SQLite en mémoire pour les tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture Pytest partagée pour créer une base de données en mémoire et une session pour chaque test.
    Assure que chaque test s'exécute sur une base de données propre et isolée.
    """
    test_db_manager = DatabaseManager(database_url=TEST_DATABASE_URL)
    test_db_manager.init_db()
    session = test_db_manager.get_session()

    yield session

    session.close()
