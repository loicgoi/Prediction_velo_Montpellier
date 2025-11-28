from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.api import app
from backend.core.dependencies import get_db_session
from backend.database.database import Prediction, CounterInfo

# TestClient allows us to send requests to our API.
client = TestClient(app)


def test_get_prediction_success(db_session: Session):
    """
    Test the success for the GET /predict endpoint.
    """

    # We override the database dependency to use our in-memory test session.
    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    # Test data is inserted into the database.
    test_counter = CounterInfo(
        id="test-predict", name="Test Predict", longitude=1, latitude=1
    )
    test_prediction = Prediction(
        counter_id="test-predict",
        prediction_date=datetime.now(),
        prediction_value=123,
        model_version="v-test",
    )
    db_session.add(test_counter)
    db_session.add(test_prediction)
    db_session.commit()

    # Send a GET request to our endpoint
    response = client.get("/predict?counter_id=test-predict")

    assert response.status_code == 200
    data = response.json()
    assert data["counter_id"] == "test-predict"
    assert data["prediction_value"] == 123
    assert data["model_version"] == "v-test"

    # Cleaning the override so as not to affect other tests
    app.dependency_overrides.clear()


def test_get_prediction_not_found(db_session: Session):
    """
    Tests the case where no counter is found for GET /predict.
    """

    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    response = client.get("/predict?counter_id=non-existent-counter")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Aucune prédiction trouvée pour le compteur non-existent-counter"
    }

    app.dependency_overrides.clear()


def test_trigger_training():
    """
    Test the POST /train endpoint.
    We cannot test whether the background task has been executed successfully,
    but we can verify that the API is responding correctly.
    """
    response = client.post("/train")
    assert response.status_code == 202  # 202 Accepted
    data = response.json()
    assert data["status"] == "training_started"
    assert "Le réentraînement du modèle a été lancé en arrière-plan" in data["message"]
