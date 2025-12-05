from .daily_update import run_daily_update
from .daily_predictor import run_prediction_pipeline
from utils.logging_config import logger


def run_full_daily_process():
    """Scheduled task: Launches data update THEN prediction."""
    logger.info("CRON START: Start of the automatic daily process.")

    try:
        logger.info("Step 1/2: Updating data...")
        run_daily_update()

        logger.info("Step 2/2: Making predictions...")
        run_prediction_pipeline()

        logger.info("CRON END: Daily process completed successfully.")

    except Exception as e:
        logger.error(f"CRON ERROR: An error occurred during the daily process: {e}")
