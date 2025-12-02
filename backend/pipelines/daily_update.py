from datetime import datetime, timedelta

from pipelines.pipeline import (
    fetch_data_for_date,
)
from pipelines.data_insertion import insert_data_to_db
from utils.logging_config import logger


def run_daily_update():
    """
    Orchestrates the daily data update pipeline.
    1. Determines the date for yesterday (J-1).
    2. Fetches data for that specific date.
    3. Inserts the fetched data into the database.
    """
    logger.info("--- Starting the daily update pipeline ---")

    # Determine yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    logger.info(f"Data targeting for the date: {yesterday.strftime('%Y-%m-%d')}")

    try:
        # Download data for D-1
        df_agg, df_weather, df_metadata = fetch_data_for_date(yesterday)

        if df_agg.empty:
            logger.warning(
                "No new traffic data found for yesterday. The pipeline stops."
            )
            return

        # Insert the new data into the database
        logger.info("Starting to insert new data...")
        insert_data_to_db(df_agg, df_weather, df_metadata)

        logger.info("Daily update pipeline successfully completed.")

    except Exception as e:
        logger.error(
            f"An error occurred during the update pipeline: {e}",
            exc_info=True,
        )
