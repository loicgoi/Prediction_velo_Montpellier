from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy.orm import Session

from backend.database.database import Prediction, CounterInfo
from backend.database.service import DatabaseService


def test_health_check(client: TestClient):
    """
    Test the base endpoint to verify that the API responds correctly.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Bienvenue sur l'API de prédiction de trafic vélo. Accédez à /docs pour la documentation."
    }


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

    response = client.get("/api/predict?counter_id=test-predict")

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
    response = client.get("/api/predict?counter_id=non-existent-counter")
    assert response.status_code == 404
    assert "Aucune prédiction trouvée" in response.json()["detail"]


def test_trigger_daily_update(client: TestClient):
    """
    Tests that the POST /api/update endpoint correctly triggers the background task.
    """
    # We use 'patch' to "spy" on the `run_daily_update` function.
    # We want to check if it's called, without actually running it.
    with patch("backend.api.endpoints.run_daily_update") as mock_run_update:
        # Act: Call the endpoint
        response = client.post("/api/update")

        # Assert: Check the response from the endpoint
        assert response.status_code == 202
        assert response.json() == {
            "status": "daily_update_started",
            "message": "La mise à jour des données de J-1 a été lancée en arrière-plan.",
        }

        # Assert: Check that our background task function was called exactly once.
        mock_run_update.assert_called_once()
