from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from typing import List, Dict, Any
from api.schema import CounterDTO

from database.service import DatabaseService
from core.dependencies import get_db_session
from core.training import run_model_training
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
        # On peut choisir de renvoyer une liste vide ou une 404,
        # mais une liste vide est souvent préférable pour le frontend.
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

    # --- CORRECTION CRITIQUE ICI ---
    # Si l'ID n'existe pas ou s'il n'y a pas de prédiction, on renvoie une 404
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
