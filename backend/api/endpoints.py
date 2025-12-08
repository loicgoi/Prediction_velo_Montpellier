from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from typing import List, Dict, Any
from api.schema import CounterDTO

from database.service import DatabaseService
from core.dependencies import get_db_session
from core.training_orchestrator import run_model_training
from pipelines.daily_update import run_daily_update
from utils.logging_config import logger

router = APIRouter()

# ----------- Metrics -----------
# Counter for /predict requests per station
predictions_counter = Counter(
    "predictions_total", "Total number of predictions made", ["station_id"]
)

# Summary for request latency on /predict
request_latency = Summary(
    "request_latency_seconds", "Latency for /predict requests in seconds"
)

# Counter for /train requests
train_counter = Counter("training_started_total", "Number of model trainings started")

# Counter for /update requests
update_counter = Counter(
    "daily_update_started_total", "Number of daily updates started"
)

# ----------- Endpoints -----------


@router.get("/counters", response_model=List[CounterDTO])
def get_counters(db: Session = Depends(get_db_session)):
    """
    Récupère la liste de tous les compteurs disponibles.
    """
    service = DatabaseService(db)
    counters = service.get_all_stations()

    if not counters:
        return []

    return counters


@router.get("/predict", summary="Get the latest prediction for a counter")
@request_latency.time()
def get_prediction(
    station_id: str, db: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Returns the most recent prediction for a given `station_id`.
    """
    # Increment prediction counter metric
    predictions_counter.labels(station_id=station_id).inc()

    service = DatabaseService(db)
    prediction = service.get_latest_prediction_for_counter(station_id)

    # If the ID does not exist or there is no prediction, a 404 is returned.
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune prédiction trouvée pour le compteur {station_id}",
        )

    # Convert the SQLAlchemy object to a dict for JSON serialization
    return {
        "id": prediction.id,
        "station_id": prediction.station_id,
        "prediction_date": prediction.prediction_date.isoformat(),
        "prediction_value": prediction.prediction_value,
        "model_version": prediction.model_version,
        "created_at": prediction.created_at.isoformat()
        if prediction.created_at
        else None,
    }


@router.post("/train", status_code=202, summary="Start model retraining")
def trigger_training(background_tasks: BackgroundTasks):
    # Increment training counter
    train_counter.inc()
    logger.info("Request for retraining received.")
    background_tasks.add_task(run_model_training)
    return {
        "status": "training_started",
        "message": "Model retraining started in background.",
    }


@router.post("/update", status_code=202, summary="Start daily data update")
def trigger_daily_update(background_tasks: BackgroundTasks):
    # Increment daily update counter
    update_counter.inc()
    logger.info("Request for daily data updates received.")
    background_tasks.add_task(run_daily_update)
    return {
        "status": "daily_update_started",
        "message": "Daily update started in background.",
    }


@router.get("/metrics")
def metrics():
    # Expose Prometheus metrics
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get("/dashboard/{station_id}")
def get_dashboard_data(station_id: str, db: Session = Depends(get_db_session)):
    """
    Aggregated endpoint for the frontend: returns Prediction of the day + History.
    """
    service = DatabaseService(db)

    # Daily prediction (D0)
    pred_today = service.get_latest_prediction_for_counter(station_id)

    # Prepare prediction info, including its date for the frontend to check freshness.
    if pred_today:
        prediction_info = {
            "value": pred_today.prediction_value,
            "date": pred_today.prediction_date.isoformat(),
        }
    else:
        # If no prediction is available at all for this counter
        prediction_info = {"value": 0, "date": None}

    # Yesterday's prediction (D-1) and yesterday's actual (D-1) for the KPI
    # We could add it in get_dashboard_stats, but we can deduce it on the front end
    # if get_dashboard_stats returns the specific lists.

    # Historical statistics
    stats = service.get_dashboard_stats(station_id)

    # We calculate the “Yesterday” KPI here to simplify the frontend.
    # We take the last value from the ‘accuracy’ lists.
    acc_real = stats["accuracy_7_days"]["real"]
    acc_pred = stats["accuracy_7_days"]["pred"]

    yesterday_real = acc_real[-1] if acc_real else 0
    yesterday_pred = acc_pred[-1] if acc_pred else 0

    return {
        "prediction": prediction_info,
        "yesterday": {"real": yesterday_real, "predicted": yesterday_pred},
        **stats,  # Unpack history, weekly_averages, etc.
    }
