from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database.database import Prediction, CounterInfo
from backend.database.service import DatabaseService


def test_health_check(client: TestClient):
    """
    Test the base endpoint to verify that the API responds correctly.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_prediction_success(client: TestClient, db_session: Session):
    """
    Test the success case for the GET /predict endpoint.
    """
    # Verify that the tables exist
    from backend.database.database import Base

    engine = db_session.get_bind()
    Base.metadata.create_all(bind=engine)  # S'assurer que les tables sont créées

    # Create the counter
    test_counter = CounterInfo(
        id="test-predict", name="Test Predict", longitude=1.0, latitude=1.0
    )
    db_session.add(test_counter)
    db_session.commit()

    # Create the prediction
    test_prediction = Prediction(
        counter_id="test-predict",
        prediction_date=datetime.now(),
        prediction_value=123,
        model_version="v-test",
    )
    db_session.add(test_prediction)
    db_session.commit()

    # Verify that the data is in the database
    counter_count = db_session.query(CounterInfo).count()
    prediction_count = db_session.query(Prediction).count()
    print(f"Counters in DB: {counter_count}, Predictions in DB: {prediction_count}")

    response = client.get("/predict?counter_id=test-predict")

    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")

    assert response.status_code == 200
    data = response.json()
    assert data["counter_id"] == "test-predict"
    assert data["prediction_value"] == 123


def test_get_prediction_not_found(client: TestClient):
    """
    Tests the case where no prediction is found for a counter.
    """
    response = client.get("/predict?counter_id=non-existent-counter")
    assert response.status_code == 404
    assert "Aucune prédiction trouvée" in response.json()["detail"]
