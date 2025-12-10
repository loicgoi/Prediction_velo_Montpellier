import pandas as pd
from utils.logging_config import logger
from core.dependencies import db_manager
from database.database import BikeCount, Weather, CounterInfo
from features.features_engineering import FeaturesEngineering
from pipelines.model_training import train_model_pipeline


def run_model_training():
    """
    Orchestrator for the monthly model retraining process.

    This function connects the production database to the modeling pipeline.
    It follows the exact process defined by the existing modules:
    1.  Loads all historical data (counts, weather, station info) from the database.
    2.  Uses the `FeaturesEngineering` class to create a rich feature set.
    3.  Passes the resulting DataFrame to the `train_model_pipeline` function,
        which handles preprocessing, training, evaluation, and saving the artifacts.
    """
    logger.info("Starting monthly model retraining orchestrator")

    try:
        # Step 1: Load all necessary data from the database
        logger.info(
            "Step 1/3: Loading data from database (BikeCount, Weather, CounterInfo)..."
        )
        with db_manager.get_session() as session:
            query_counts = session.query(BikeCount).statement
            query_weather = session.query(Weather).statement
            query_info = session.query(CounterInfo).statement

            df_counts = pd.read_sql(query_counts, session.bind)
            df_weather = pd.read_sql(query_weather, session.bind)
            df_info = pd.read_sql(query_info, session.bind)

        if df_counts.empty or df_weather.empty or df_info.empty:
            logger.error("No data found in database. Aborting training.")
            return

        # Merge datasets to create a single comprehensive DataFrame
        df = pd.merge(df_counts, df_weather, on="date", how="inner")
        df = pd.merge(df, df_info, on="station_id", how="left")
        logger.info(f"Loaded and merged {len(df)} rows of data.")

        # Step 2: Use the existing FeaturesEngineering class
        logger.info("Step 2/3: Applying feature engineering pipeline...")

        if "avg_temp" not in df.columns and "temperature_2m_max" in df.columns:
            df["avg_temp"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
            logger.info("Created 'avg_temp' column.")

        df.rename(columns={"precipitation_sum": "precipitation_mm"}, inplace=True)

        # Chain all feature engineering steps as defined by the colleague
        feature_builder = FeaturesEngineering(df)
        processed_df = (
            feature_builder.remove_suspect_counters()
            .add_week_month_year()
            .Cycliques()
            .add_holidays_feature()
            .add_weather_featuers()
            .lag()
            .get_data()
        )

        logger.info("Feature engineering complete.")

        # Step 3: Hand over to the complete training pipeline
        logger.info("Step 3/3: Starting the model training pipeline...")
        train_model_pipeline(processed_df)

        logger.info("Monthly model retraining orchestrator finished successfully.")

    except Exception as e:
        logger.error(f"An error occurred during model training: {e}", exc_info=True)
