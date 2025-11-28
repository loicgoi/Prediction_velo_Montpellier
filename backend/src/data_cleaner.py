import pandas as pd
from pandas import DataFrame
from utils.logging_config import logger


def drop_duplicate(df: DataFrame) -> DataFrame:
    """
    Remove duplicated rows from the DataFrame.

    Args:
        df (DataFrame): Input DataFrame possibly containing duplicates.

    Returns:
        DataFrame: New DataFrame with duplicate rows removed.
    """
    print(f"Data amount before dropping duplicates: {len(df)}")
    logger.info(f"Data amount before dropping duplicates: {len(df)}")

    df_cleaned: DataFrame = df.copy().drop_duplicates()

    print(f"Data amount after dropping duplicates: {len(df_cleaned)}")
    logger.info(f"Data amount after dropping duplicates: {len(df_cleaned)}")

    return df_cleaned


def agregate(df: DataFrame) -> DataFrame:
    """
    Aggregate trafic data daily per station.

    Steps:
        - Convert 'date' column to datetime
        - Set 'date' as index
        - Group by 'station_id' and resample daily, summing 'intensity'

    Args:
        df (DataFrame): Input trafic DataFrame with columns 'station_id', 'date', 'intensity'.

    Returns:
        DataFrame: Aggregated DataFrame with daily intensity per station.
    """
    print(f"Data amount before aggregation: {df.shape}")
    logger.info(f"Data amount before aggregation: {df.shape}")

    df_copy: DataFrame = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.set_index("date")
    df_agg: DataFrame = (
        df_copy.groupby("station_id").resample("D")["intensity"].sum().reset_index()
    )

    print(f"Data amount after aggregation: {df_agg.shape}")
    logger.info(f"Data amount after aggregation: {df_agg.shape}")

    print(f"Sample after aggregation:\n{df_agg.head(5)}")
    logger.info(f"Sample after aggregation:\n{df_agg.head(5)}")

    return df_agg
