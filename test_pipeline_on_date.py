import sys
from datetime import datetime, timedelta

try:
    from freezegun import freeze_time
except ImportError:
    print("Error: 'freezegun' is not installed. Please run 'pip install freezegun'")
    sys.exit(1)

# Add backend to path to allow imports from the application
sys.path.append("./backend")

from pipelines.daily_update import run_daily_update
from pipelines.daily_predictor import run_prediction_pipeline
from utils.logging_config import logger


def run_test_for_date(date_str: str):
    """
    Simulates the full daily process (data update + prediction) for a specific historical date.

    This script will:
    1. Freeze time to the day AFTER the target date.
    2. Run the daily update, which will fetch data for the target date (as "yesterday").
    3. Run the prediction pipeline, which will generate predictions for the day AFTER the target date.

    Args:
        date_str (str): The date for which to fetch data, in "YYYY-MM-DD" format.
    """
    try:
        target_data_date = datetime.strptime(date_str, "%Y-%m-%d")
        simulation_date = target_data_date + timedelta(days=1)
        simulation_date_str = simulation_date.strftime("%Y-%m-%d")

        logger.info(f"--- Starting test pipeline for data date: {date_str} ---")
        logger.info(f"--- Simulating current time as: {simulation_date_str} ---")

        with freeze_time(simulation_date_str):
            logger.info(f"--- Running daily update to fetch data for {date_str} ---")
            run_daily_update()

            logger.info(
                f"--- Running prediction pipeline for {simulation_date_str} ---"
            )
            run_prediction_pipeline()

        logger.info(f"--- Test pipeline completed for {date_str}. ---")
        logger.info(
            f"Check the 'prediction' table for entries with prediction_date = {simulation_date_str}."
        )

    except Exception as e:
        logger.error(f"An error occurred during the test pipeline: {e}", exc_info=True)


if __name__ == "__main__":
    target_date_to_test = "2025-11-30"
    run_test_for_date(target_date_to_test)
