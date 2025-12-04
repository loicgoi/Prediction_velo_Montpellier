from datetime import datetime, timedelta
from pipelines.pipeline import fetch_data_for_date
from download.daily_weather_api import OpenMeteoDailyAPIC
from src.api_data_processing import extract_daily_weather
from pipelines.data_insertion import insert_data_to_db
from utils.logging_config import logger


def run_daily_update():
    """
    Orchestrates the daily update pipeline.

    Steps:
    1. Determines yesterday's date (J-1).
    2. Fetches traffic, metadata, and initial weather data for that date using fetch_data_for_date().
    3. Fetches additional daily weather from OpenMeteo API and converts it to a DataFrame.
    4. Inserts all available dataframes into the database separately with detailed logging.
    """

    logger.info("--- Starting the daily update pipeline ---")

    # Step 1: Determine yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    logger.info(f"Data targeting for the date: {date_str}")

    try:
        # Step 2: Fetch traffic, metadata, and initial weather data
        df_agg, df_weather, df_metadata = fetch_data_for_date(yesterday)
        logger.info(
            "Fetched traffic and initial weather data using fetch_data_for_date()."
        )

        # Step 3: Fetch additional daily weather using OpenMeteo API
        logger.info("Fetching additional daily weather data from OpenMeteo API...")
        client = OpenMeteoDailyAPIC()
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        json_response = client.get_weather_json(
            latitude=43.6109, longitude=3.8763, start_date=today_str, end_date=today_str
        )
        df_daily_weather = extract_daily_weather(json_response)
        logger.info(
            f"OpenMeteo daily weather data fetched. Rows: {len(df_daily_weather)}"
        )

        # Step 4: Prepare dataframes for insertion
        dataframes_to_insert = [
            ("Traffic Data", df_agg, df_weather, df_metadata),
            ("OpenMeteo Daily Weather", None, df_daily_weather, None),
        ]

        # Step 5: Insert each dataframe separately (i used loop to avoid repeating the function insert_data_to_db on the 2 API sources)
        for name, traffic_df, weather_df, metadata_df in dataframes_to_insert:
            if (
                (traffic_df is not None and not traffic_df.empty)
                or (weather_df is not None and not weather_df.empty)
                or (metadata_df is not None and not metadata_df.empty)
            ):
                logger.info(f"Inserting {name} into database...")
                insert_data_to_db(traffic_df, weather_df, metadata_df)
                logger.info(f"{name} successfully inserted.")
            else:
                logger.warning(f"{name} is empty or None. Skipping insertion.")

        logger.info("Daily update pipeline successfully completed.")

    except Exception as e:
        logger.error(
            f"An error occurred during the update pipeline: {e}", exc_info=True
        )
