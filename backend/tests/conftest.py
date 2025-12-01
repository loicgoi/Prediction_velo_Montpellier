import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.api.api import app as main_app
from backend.core.dependencies import get_db_session
from backend.database.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    """
    Fixture that creates an isolated in-memory test database for each test.
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Fixture to create a TestClient that uses the test database.
    """

    def override_get_db_session():
        try:
            yield db_session
        finally:
            # Do not close the session here, it is managed by the db_session fixture.
            pass

    # Replace the dependency to use our test session
    main_app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(main_app) as test_client:
        yield test_client

    # Clean up overrides
    main_app.dependency_overrides.clear()
