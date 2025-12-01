import pandas as pd
from dotenv import load_dotenv

from backend.database.database import DatabaseManager
from backend.database.service import DatabaseService
from backend.utils.logging_config import logger


def insert_data_to_db(
    df_trafic: pd.DataFrame, df_weather: pd.DataFrame, df_metadata: pd.DataFrame
):
    """
    Connects to the database and inserts data from DataFrames.

    :param df_trafic: DataFrame with bike count data.
    :param df_weather: DataFrame with weather data.
    :param df_metadata: DataFrame with counter metadata.
    """
    # Load environment variables to get DATABASE_URL
    load_dotenv()

    # Setup database connection
    logger.info("Connecting to the database for data insertion...")
    db_manager = DatabaseManager()
    session = db_manager.get_session()

    try:
        service = DatabaseService(session)

        # Convert DataFrames to list of dictionaries
        # The service layer expects data in this format.
        counters_data = df_metadata.to_dict(orient="records")
        counts_data = df_trafic.to_dict(orient="records")
        weather_data = df_weather.to_dict(orient="records")

        # Call service methods to insert data
        logger.info("Inserting counter metadata...")
        service.add_counter_infos(counters_data)

        logger.info("Inserting bike counts...")
        service.add_bike_counts(counts_data)

        logger.info("Inserting weather data...")
        service.add_weather_data(weather_data)

        logger.info("Data insertion process completed successfully.")
    finally:
        # Ensure the session is closed
        session.close()
