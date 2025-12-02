from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database.service import DatabaseService
from core.dependencies import get_db_session
from core.training import run_model_training
from pipelines.daily_update import run_daily_update
from utils.logging_config import logger

router = APIRouter()


@router.get("/predict", summary="Récupérer la dernière prédiction pour un compteur")
def get_prediction(station_id: str, db: Session = Depends(get_db_session)):
    """
    Returns the most recent prediction for a given `counter_id`.
    """
    service = DatabaseService(db)
    prediction = service.get_latest_prediction_for_counter(station_id)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No predictions found for the counter {station_id}",
        )

    # Convert the SQLAlchemy object to a dict for JSON serialization
    return {
        "id": prediction.id,
        "station_id": prediction.station_id,
        "prediction_date": prediction.prediction_date.isoformat(),
        "prediction_value": prediction.prediction_value,
        "model_version": prediction.model_version,
        "created_at": prediction.created_at.isoformat()
        if prediction.created_at  # type: ignore
        else None,
    }


@router.post("/train", status_code=202, summary="Lancer un réentraînement du modèle")
def trigger_training(background_tasks: BackgroundTasks):
    logger.info("Request for retraining received.")
    background_tasks.add_task(run_model_training)
    return {
        "status": "training_started",
        "message": "Le réentraînement du modèle a été lancé en arrière-plan.",
    }


@router.post(
    "/update",
    status_code=202,
    summary="Lancer la mise à jour quotidienne des données",
)
def trigger_daily_update(background_tasks: BackgroundTasks):
    logger.info("Request for daily data updates received.")
    background_tasks.add_task(run_daily_update)
    return {
        "status": "daily_update_started",
        "message": "La mise à jour des données de J-1 a été lancée en arrière-plan.",
    }
