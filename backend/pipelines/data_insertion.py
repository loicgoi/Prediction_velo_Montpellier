import pandas as pd
from database.service import DatabaseService
from sqlalchemy.exc import SQLAlchemyError
from core.dependencies import db_manager
from utils.logging_config import logger


def insert_data_to_db(
    df_agg: pd.DataFrame = None, 
    df_weather: pd.DataFrame = None, 
    df_metadata: pd.DataFrame = None
):
    """
    Inserts data into the database. Handles None inputs safely.
    """
    # Setup database connection
    logger.info("Getting a database session...")
    session = db_manager.get_session()

    try:
        service = DatabaseService(session)

        # 1. Counters (Metadata)
        if df_metadata is not None and not df_metadata.empty:
            counters_data = df_metadata.to_dict(orient="records")
            logger.info(f"Envoi de {len(counters_data)} compteurs...") 
            service.add_counter_infos(counters_data)
        else:
            logger.info("No metadata to insert (None or empty).")

        # 2. Traffic (BikeCount)
        if df_agg is not None and not df_agg.empty:
            counts_data = df_agg.to_dict(orient="records")
            logger.info(f"Envoi de {len(counts_data)} données de trafic...") 
            service.add_bike_counts(counts_data)
        else:
            logger.info("No traffic data to insert.")

        # 3. Weather
        if df_weather is not None and not df_weather.empty:
            weather_data = df_weather.to_dict(orient="records")
            logger.info(f"Envoi de {len(weather_data)} données météo...") 
            service.add_weather_data(weather_data)
        else:
            logger.info("No weather data to insert.")

        logger.info("Commit transaction...")
        session.commit()
        logger.info("Data insertion process completed successfully.")

    except SQLAlchemyError as e:
        logger.error(f"A database error has occurred: {e}", exc_info=True)
        session.rollback()
    except Exception as e:
        logger.error(f"An unexpected error has occurred: {e}", exc_info=True)
    finally:
        session.close()
        logger.info("Session closed.")