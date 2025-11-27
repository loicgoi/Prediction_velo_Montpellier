import pytest
from datetime import datetime
from database.database import DatabaseManager, CounterInfo, BikeCount


@pytest.fixture(scope="module")
def db_session():
    """Fixture for creating an in-memory database for testing."""
    db_manager = DatabaseManager(database_url="sqlite:///:memory:")
    db_manager.init_db()
    session = db_manager.get_session()
    yield session
    session.close()


def test_create_and_read_counter(db_session):
    """Tests the creation and reading of a CounterInfo."""
    new_counter = CounterInfo(
        id="PYTEST01", name="Compteur Pytest", longitude=1.0, latitude=1.0
    )
    db_session.add(new_counter)
    db_session.commit()

    retrieved = db_session.query(CounterInfo).filter_by(id="PYTEST01").first()
    assert retrieved is not None
    assert retrieved.name == "Compteur Pytest"


def test_create_and_read_bike_count(db_session):
    """Test the creation and reading of a BikeCount."""
    if not db_session.query(CounterInfo).filter_by(id="PYTEST01").first():
        test_create_and_read_counter(db_session)

    new_count = BikeCount(
        date=datetime.now(),
        counter_id="PYTEST01",
        intensity=99,
    )
    db_session.add(new_count)
    db_session.commit()

    retrieved = db_session.query(BikeCount).filter_by(counter_id="PYTEST01").first()
    assert retrieved is not None
    assert retrieved.intensity == 99
