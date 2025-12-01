from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
import pytest, typing
from sqlalchemy import create_engine
from sqlalchemy import text

from backend.database.database import (
    CounterInfo,
    BikeCount,
    Weather,
    Prediction,
    ModelMetrics,
    Base,
)
from backend.database.service import DatabaseService

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Fixture dédiée aux tests de service, fournissant une session de DB isolée.
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_add_counter_infos_success(db_session: Session):
    """
    Tests the successful addition of new counters that do not yet exist.
    """
    service = DatabaseService(db_session)
    counters_to_add = [
        {
            "id": "counter-01",
            "name": "Albert 1er",
            "longitude": 3.87,
            "latitude": 43.61,
        },
        {"id": "counter-02", "name": "Lattes", "longitude": 3.90, "latitude": 43.56},
    ]

    success = service.add_counter_infos(counters_to_add)

    assert success is True

    count = db_session.execute(text("SELECT COUNT(*) FROM counters_info")).scalar_one()

    assert count == 2


def test_add_counter_infos_handles_duplicates(db_session: Session):
    """
    Tests that counters with existing coordinates (lon, lat) are not added.
    """
    # Insert a first counter
    initial_counter = CounterInfo(
        id="initial-01", name="Place de la Comédie", longitude=3.879, latitude=43.608
    )
    db_session.add(initial_counter)
    db_session.commit()

    service = DatabaseService(db_session)
    counters_to_add = [
        # This counter is a duplicate based on the coordinates.
        {
            "id": "duplicate-id",
            "name": "Doublon Comédie",
            "longitude": 3.879,
            "latitude": 43.608,
        },
        # This counter is really new.
        {"id": "new-02", "name": "Odysseum", "longitude": 3.91, "latitude": 43.60},
    ]

    success = service.add_counter_infos(counters_to_add)

    assert success is True

    count = db_session.execute(text("SELECT COUNT(*) FROM counters_info")).scalar_one()

    assert count == 2

    new_entry = db_session.query(CounterInfo).filter_by(id="new-02").one_or_none()

    assert new_entry is not None
    assert new_entry.name == "Odysseum"  # type: ignore


def test_add_bike_counts_success(db_session: Session):
    """Tests adding count data via the generic _bulk_add method."""
    service = DatabaseService(db_session)
    counts_to_add = [
        {
            "date": datetime.fromisoformat("2023-10-27"),
            "counter_id": "counter-01",
            "intensity": 100,
        },
        {
            "date": datetime.fromisoformat("2023-10-28"),
            "counter_id": "counter-01",
            "intensity": 150,
        },
    ]

    success = service.add_bike_counts(counts_to_add)

    assert success is True
    assert db_session.query(BikeCount).count() == 2


def test_add_weather_data_success(db_session: Session):
    """Tests adding weather data."""
    service = DatabaseService(db_session)
    weather_to_add = [
        {
            "date": datetime.fromisoformat("2023-10-27T12:00:00"),
            "avg_temp": 15.5,
            "precipitation_mm": 0.5,
            "vent_max": 25.0,
        },
        {
            "date": datetime.fromisoformat("2023-10-28T12:00:00"),
            "avg_temp": 14.0,
            "precipitation_mm": 2.0,
            "vent_max": 30.0,
        },
    ]

    success = service.add_weather_data(weather_to_add)

    assert success is True
    assert db_session.query(Weather).count() == 2


def test_add_predictions_success(db_session: Session):
    """Tests adding prediction data."""
    # A counter must exist for the foreign key constraint
    counter = CounterInfo(
        id="pred-counter", name="Prediction Counter", longitude=5.0, latitude=45.0
    )
    db_session.add(counter)
    db_session.commit()

    service = DatabaseService(db_session)
    predictions_to_add = [
        {
            "prediction_date": datetime.fromisoformat("2024-01-01T10:00:00"),
            "counter_id": "pred-counter",
            "prediction_value": 200,
            "model_version": "v1.0",
        }
    ]

    success = service.add_predictions(predictions_to_add)

    assert success is True
    assert db_session.query(Prediction).count() == 1
    assert db_session.query(Prediction).first().prediction_value == 200  # type: ignore


def test_add_model_metrics_success(db_session: Session):
    """Tests adding model metrics data."""
    # A counter must exist for the foreign key constraint
    counter = CounterInfo(
        id="metrics-counter", name="Metrics Counter", longitude=6.0, latitude=46.0
    )
    db_session.add(counter)
    db_session.commit()

    service = DatabaseService(db_session)
    metrics_to_add = [
        {
            "counter_id": "metrics-counter",
            "date": datetime.fromisoformat("2024-01-01T10:00:00"),
            "actual_value": 150,
            "predicted_value": 145,
            "model_version": "v1.1",
        }
    ]

    success = service.add_model_metrics(metrics_to_add)

    assert success is True
    assert db_session.query(ModelMetrics).count() == 1
    assert db_session.query(ModelMetrics).first().actual_value == 150  # type: ignore
