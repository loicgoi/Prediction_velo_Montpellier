from download.ecocounters_ids import EncountersIDsLoader
from download.weeather_api import WeatherHistoryLoader
from src.data_exploration import Statistics
from src.data_cleaner import drop_duplicate, agregate
from src.api_data_processing import (
    extract_station_metadata,
    fetch_and_extract_timeseries,
    extract_weather_fields,
)
from src.data_merger import (
    merge_trafic_with_metadata,
    merge_trafic_with_weather,
)
from features.features_engineering import FeaturesEngineering
import pandas as pd
from core.dependencies import db_manager
from pipelines.data_insertion import insert_data_to_db
from utils.logging_config import logger


def fetch_data_from_apis():
    """Fetch trafic, weather, and metadata from APIs"""
    logger.info("STEP 1 - Fetching data from APIs...")
    print("Fetching data...")

    try:
        df_metadata, ids = extract_station_metadata(EncountersIDsLoader().fetch_data())
        logger.info(f"Fetched metadata. Number of stations: {len(ids)}")

        if not ids:
            logger.warning("No station IDs returned from API.")
            print("No station IDs found.")
            return None, None, None

        df_trafic = fetch_and_extract_timeseries(ids)
        logger.info("Fetched trafic time-series.")

        df_weather = extract_weather_fields(WeatherHistoryLoader().fetch_data())
        logger.info("Fetched weather data.")

        print("Data fetching done.\n")
        logger.info("API data fetching completed successfully.")
        return df_trafic, df_weather, df_metadata

    except Exception as e:
        logger.error(f"Error fetching data from APIs: {e}")
        return None, None, None


def explore_data(df_trafic, df_weather):
    """Explore trafic and weather data"""
    logger.info("STEP 2 - Exploring data...")
    print("Exploring data...\n")

    try:
        stats = Statistics(
            [df_trafic, df_weather], names=["Trafic History", "Weather History"]
        )
        stats.info()
        stats.describe()
        stats.isna()
        stats.duplicated()

        print("Data exploration done.\n")
        logger.info("Data exploration completed successfully.")

    except Exception as e:
        logger.error(f"Error while exploring data: {e}")


def clean_and_aggregate(df_trafic):
    """Drop duplicates and aggregate trafic data"""
    logger.info("STEP 3 - Cleaning and aggregating trafic data...")

    try:
        df_clean = drop_duplicate(df_trafic)
        logger.info("Duplicates dropped.")

        df_agg = agregate(df_clean)
        logger.info("Aggregation completed.")

        print("Data aggregation done.\n")
        return df_agg

    except Exception as e:
        logger.error(f"Error during cleaning/aggregation: {e}")
        return None


def insert_data_into_db(df_agg, df_weather, df_metadata) -> bool:
    """
    Inserts aggregated trafic data, weather data, and metadata into the database.
    Returns True if insertion succeeds, False otherwise.
    """
    logger.info("STEP 4 - Starting database insertion process...")
    print("STEP 4 - Starting database insertion process...")
    if df_agg is None or df_weather is None or df_metadata is None:
        logger.warning("One or more dataframes are None. Skipping DB insertion.")
        return False

    # Initialize DB tables if not created
    try:
        logger.info("Initializing database structure...")
        print("Initializing database structure...")
        db_manager.init_db()
        logger.info("Database initialized successfully.")
        print("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error during DB initialization: {e}")
        print(f"Critical error during DB initialization: {e}")
        return False

    # Insert data
    try:
        logger.info("Inserting trafic, weather, and metadata into DB...")
        print("Inserting trafic, weather, and metadata into DB...")
        insert_data_to_db(df_agg, df_weather, df_metadata)
        logger.info("Database insertion completed successfully.")
        print("Database insertion completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error while inserting data into DB: {e}")
        print(f"Error while inserting data into DB: {e}")
        return False


def merge_data(df_agg, df_metadata, df_weather):
    """Merge trafic, metadata, and weather"""
    logger.info("STEP 5 - Merging datasets...")

    try:
        df_trafic_coords = merge_trafic_with_metadata(df_agg, df_metadata)
        logger.info("Merged trafic with metadata.")

        df_final = merge_trafic_with_weather(df_trafic_coords, df_weather)
        logger.info("Merged trafic+metadata with weather.")

        print(f"Data merged. Final shape: {df_final.shape}")
        logger.info(f"Data merge completed. Final shape: {df_final.shape}")
        return df_final

    except Exception as e:
        logger.error(f"Error while merging data: {e}")
        return None


def run_features_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering to the final merged dataset.
    Returns the processed dataframe ready for modeling.
    """
    logger.info("STEP 6 - Running feature engineering...")

    if df is None:
        logger.error("No dataframe provided for feature engineering.")
        print("[ERROR] No data provided for feature engineering.")
        return pd.DataFrame()

    try:
        print("[STEP] Running feature engineering...")
        fe = FeaturesEngineering(df)

        fe.add_week_month_year().Cycliques().add_weather_featuers().lag().add_holidays_feature().remove_suspect_counters()

        final_df_features = fe.get_data()
        fe.save_to_csv(filename="features_ready_for_training.csv")

        print("[INFO] Feature engineering completed. Sample:")
        print(final_df_features.head(2))

        logger.info("Feature engineering completed successfully.")
        return final_df_features

    except Exception as e:
        logger.error(f"Error during feature engineering: {e}")
        return pd.DataFrame()
