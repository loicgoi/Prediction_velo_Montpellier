import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database.service import DatabaseService
from backend.core.dependencies import get_db_session
from backend.core.training import run_model_training

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predict", summary="Récupérer la dernière prédiction pour un compteur")
def get_prediction(counter_id: str, db: Session = Depends(get_db_session)):
    """
    Returns the most recent prediction for a given `counter_id`.
    """
    service = DatabaseService(db)
    prediction = service.get_latest_prediction_for_counter(counter_id)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune prédiction trouvée pour le compteur {counter_id}",
        )
    return prediction


@router.post("/train", status_code=202, summary="Lancer un réentraînement du modèle")
def trigger_training(background_tasks: BackgroundTasks):
    """
    Triggers a retraining of the model in the background.
    """
    logger.info("Requête de réentraînement reçue.")
    background_tasks.add_task(run_model_training)
    return {
        "status": "training_started",
        "message": "Le réentraînement du modèle a été lancé en arrière-plan.",
    }
