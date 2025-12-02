import pandas as pd
from database.service import DatabaseService
from sqlalchemy.exc import SQLAlchemyError
from core.dependencies import db_manager
from utils.logging_config import logger


def insert_data_to_db(
    df_trafic: pd.DataFrame, df_weather: pd.DataFrame, df_metadata: pd.DataFrame
):
    print("[DEBUG] Début de insert_data_to_db...")

    # Setup database connection
    logger.info("Obtention d'une session de base de données...")
    session = db_manager.get_session()

    try:
        service = DatabaseService(session)

        print("[DEBUG] Conversion des DataFrames en dictionnaires...")
        counters_data = df_metadata.to_dict(orient="records")
        counts_data = df_trafic.to_dict(orient="records")
        weather_data = df_weather.to_dict(orient="records")

        # Call service methods
        print(f"[DEBUG] Envoi de {len(counters_data)} compteurs...")
        service.add_counter_infos(counters_data)

        print(f"[DEBUG] Envoi de {len(counts_data)} données de trafic...")
        service.add_bike_counts(counts_data)

        print(f"[DEBUG] Envoi de {len(weather_data)} données météo...")
        service.add_weather_data(weather_data)

        print("[DEBUG] Commit de la transaction (enregistrement sur Azure)...")
        session.commit()

        print("[DEBUG] SUCCÈS TOTAL de l'insertion !")
        logger.info("Data insertion process completed successfully.")

    except SQLAlchemyError as e:
        print(f"[ERREUR SQL] : {e}")
        logger.error(f"Une erreur de base de données est survenue: {e}", exc_info=True)
        session.rollback()
    except Exception as e:
        print(f"[ERREUR GÉNÉRALE] : {e}")
        logger.error(f"Une erreur inattendue est survenue: {e}", exc_info=True)
    finally:
        session.close()
        print("[DEBUG] Session fermée.")
