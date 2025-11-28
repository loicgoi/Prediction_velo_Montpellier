import pandas as pd
from pandas import DataFrame
from utils.paths import OUTPUT_PATH
from utils.logging_config import logger


def merge_trafic_with_metadata(df_agg: DataFrame, df_metadata: DataFrame) -> DataFrame:
    """
    Merge aggregated trafic data with station metadata on 'station_id'.

    Args:
        df_agg (DataFrame): Aggregated trafic data (from data_cleaner).
        df_metadata (DataFrame): Metadata of stations (from extract_station_metadata).

    Returns:
        DataFrame: Merged trafic data with station coordinates.
    """
    print("Merging trafic data with station metadata...")
    logger.info("Starting merge: trafic data with metadata.")

    df_merged = pd.merge(df_agg, df_metadata, on="station_id", how="left")

    print(f"Merged trafic & metadata shape: {df_merged.shape}")
    logger.info(f"Merged trafic & metadata shape: {df_merged.shape}")

    print("Sample of merged trafic & metadata:")
    print(df_merged.head(5))
    logger.info(f"Sample:\n{df_merged.head(5)}")

    return df_merged


def merge_trafic_with_weather(
    df_trafic_coords: DataFrame, df_weather: DataFrame
) -> DataFrame:
    """
    Merge trafic data (with station coordinates) with weather data on 'date'.

    Args:
        df_trafic_coords (DataFrame): Trafic data merged with station metadata.
        df_weather (DataFrame): Weather data extracted from API.

    Returns:
        DataFrame: Final merged DataFrame with trafic, coordinates, and weather.
    """
    print("Merging trafic data with weather data...")
    logger.info("Starting merge: trafic data with weather data.")

    # Ensure date columns are datetime and normalized
    df_trafic_coords = df_trafic_coords.copy()
    df_weather = df_weather.copy()

    df_trafic_coords["date"] = pd.to_datetime(df_trafic_coords["date"])
    df_weather["date"] = pd.to_datetime(df_weather["date"])

    try:
        df_trafic_coords["date"] = (
            df_trafic_coords["date"].dt.tz_localize(None).dt.normalize()
        )
    except TypeError:
        df_trafic_coords["date"] = df_trafic_coords["date"].dt.normalize()

    try:
        df_weather["date"] = df_weather["date"].dt.tz_localize(None).dt.normalize()
    except TypeError:
        df_weather["date"] = df_weather["date"].dt.normalize()

    df_final = pd.merge(df_trafic_coords, df_weather, on="date", how="left")

    print(f"Final merged data shape: {df_final.shape}")
    logger.info(f"Final merged data shape: {df_final.shape}")

    print("Sample of final merged data:")
    print(df_final.head(5))
    logger.info(f"Sample:\n{df_final.head(5)}")

    output_file = OUTPUT_PATH / "dataset_final.csv"
    df_final.to_csv(output_file, index=False)
    print(f"Final dataset saved at: {output_file}")
    logger.info(f"Final dataset saved at: {output_file}")

    return df_final
