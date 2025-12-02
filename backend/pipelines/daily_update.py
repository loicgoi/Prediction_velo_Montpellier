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
    logger.info("--- Démarrage du pipeline de mise à jour quotidienne ---")

    # Determine yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    logger.info(f"Ciblage des données pour la date : {yesterday.strftime('%Y-%m-%d')}")

    try:
        # Download data for D-1
        df_agg, df_weather, df_metadata = fetch_data_for_date(yesterday)

        if df_agg.empty:
            logger.warning(
                "Aucune nouvelle donnée de trafic trouvée pour hier. Le pipeline s'arrête."
            )
            return

        # Insert the new data into the database
        logger.info("Lancement de l'insertion des nouvelles données...")
        insert_data_to_db(df_agg, df_weather, df_metadata)

        logger.info("Pipeline de mise à jour quotidienne terminé avec succès.")

    except Exception as e:
        logger.error(
            f"Une erreur est survenue durant le pipeline de mise à jour : {e}",
            exc_info=True,
        )
