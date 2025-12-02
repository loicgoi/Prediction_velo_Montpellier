import pandas as pd
from database.service import DatabaseService
from sqlalchemy.exc import SQLAlchemyError
from core.dependencies import db_manager
from utils.logging_config import logger


def insert_data_to_db(
    df_agg: pd.DataFrame, df_weather: pd.DataFrame, df_metadata: pd.DataFrame
):
    # Setup database connection
    logger.info("Obtention d'une session de base de données...")
    session = db_manager.get_session()

    try:
        service = DatabaseService(session)

        logger.info("Conversion des DataFrames en dictionnaires...")
        counters_data = df_metadata.to_dict(orient="records")
        counts_data = df_agg.to_dict(orient="records")
        weather_data = df_weather.to_dict(orient="records")

        # Call service methods
        logger.info(f"Envoi de {len(counters_data)} compteurs...")
        service.add_counter_infos(counters_data)

        logger.info(f"Envoi de {len(counts_data)} données de trafic...")
        service.add_bike_counts(counts_data)

        logger.info(f"Envoi de {len(weather_data)} données météo...")
        service.add_weather_data(weather_data)

        logger.info("Commit de la transaction (enregistrement sur Azure)...")
        session.commit()

        logger.info("Data insertion process completed successfully.")

    except SQLAlchemyError as e:
        logger.error(f"Une erreur de base de données est survenue: {e}", exc_info=True)
        session.rollback()
    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue: {e}", exc_info=True)
    finally:
        session.close()
        logger.info("Session fermée.")
