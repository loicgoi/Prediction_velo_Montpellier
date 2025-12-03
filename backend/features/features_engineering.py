import pandas as pd
import numpy as np
import holidays
from utils.paths import OUTPUT_PATH


class FeaturesEngineering:
    """
    Class responsible for creating, transforming and enriching features
    for machine learning model training.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the class with a copy of the dataframe.

        Args:
            df (pd.DataFrame): Input dataset containing at least a 'date' column.
        """
        self.df: pd.DataFrame = df.copy()
        print(
            "[INFO] FeaturesEngineering initialized with dataframe of shape:",
            self.df.shape,
        )
        
        # -----------------------------------------------------------
    def remove_suspect_counters(self, suspects: list = None) -> "FeaturesEngineering":
        """
        Removes rows corresponding to a list of suspect station IDs.
        
        Args:
            suspects (list): List of station_id strings to remove. 
                             If None, uses a default hardcoded list.
        
        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Removing suspect counters...")
        
        # Liste par défaut fournie dans ta demande
        if suspects is None:
            suspects = [
                "urn:ngsi-ld:EcoCounter:867228050089043",
                "urn:ngsi-ld:EcoCounter:867228050089159",
                "urn:ngsi-ld:EcoCounter:867228050089217",
                "urn:ngsi-ld:EcoCounter:867228050089787",
                "urn:ngsi-ld:EcoCounter:867228050092989"
            ]

        # On compte avant pour le log
        initial_count = len(self.df)
        
        # Le tilde (~) signifie "NOT" en Pandas
        # On garde tout ce qui N'EST PAS dans la liste des suspects
        self.df = self.df[~self.df['station_id'].isin(suspects)]
        
        removed_count = initial_count - len(self.df)
        
        print(f"[INFO] Removed {removed_count} rows from suspect counters.")
        print(f"[INFO] New dataframe shape: {self.df.shape}")
        
        return self

    # -----------------------------------------------------------
    def add_week_month_year(self) -> "FeaturesEngineering":
        """
        Extract date-related features: day_of_week, month, year,
        day_of_year, and is_weekend.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Adding week, month, year features...")

        self.df["date"] = pd.to_datetime(self.df["date"])

        self.df["day_of_week"] = self.df["date"].dt.dayofweek
        self.df["month"] = self.df["date"].dt.month
        self.df["year"] = self.df["date"].dt.year
        self.df["day_of_year"] = self.df["date"].dt.dayofyear
        self.df["is_weekend"] = self.df["day_of_week"].isin([5, 6]).astype(int)

        print("[INFO] Added date decomposition features. Sample:")
        print(self.df.head(2))
        return self

    # -----------------------------------------------------------
    def Cycliques(self) -> "FeaturesEngineering":
        """
        Add cyclical encoding for day_of_week and month.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Adding cyclical features...")

        self.df["day_of_week_sin"] = np.sin(2 * np.pi * self.df["day_of_week"] / 7)
        self.df["day_of_week_cos"] = np.cos(2 * np.pi * self.df["day_of_week"] / 7)

        self.df["month_sin"] = np.sin(2 * np.pi * (self.df["month"] - 1) / 12)
        self.df["month_cos"] = np.cos(2 * np.pi * (self.df["month"] - 1) / 12)

        print("[INFO] Added cyclical features. Sample:")
        print(self.df.head(2))
        return self

    # -----------------------------------------------------------
    def add_weather_featuers(self) -> "FeaturesEngineering":
        """
        Create weather-based binary features from precipitation,
        temperature and wind.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Adding weather features...")

        self.df["is_rainy"] = (self.df["precipitation_mm"] > 1.0).astype(int)
        self.df["is_cold"] = (self.df["avg_temp"] < 5.0).astype(int)
        self.df["is_hot"] = (self.df["avg_temp"] > 30.0).astype(int)
        self.df["is_windy"] = (self.df["vent_max"] > 30.0).astype(int)

        print("[INFO] Added weather features. Sample:")
        print(self.df.head(2))
        return self

    # -----------------------------------------------------------
    def lag(self) -> "FeaturesEngineering":
        """
        Add lag features (lag_1 and lag_7) grouped by station_id.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Adding lag features...")

        self.df = self.df.sort_values(by=["station_id", "date"])

        self.df["lag_1"] = self.df.groupby("station_id")["intensity"].shift(1)
        self.df["lag_7"] = self.df.groupby("station_id")["intensity"].shift(7)

        # drop rows with missing lags
        self.df = self.df.dropna(subset=["lag_1", "lag_7"])

        print("[INFO] Lag features added.")
        return self

    # -----------------------------------------------------------
    def add_holidays_feature(self) -> "FeaturesEngineering":
        """
        Add a boolean 'is_holiday' feature using French official holidays.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Adding holiday feature...")

        self.df["date"] = pd.to_datetime(self.df["date"])
        years = self.df["date"].dt.year.unique()
        year_range = range(min(years), max(years) + 2)

        fr_holidays = holidays.FR(years=year_range)
        self.holidays = fr_holidays

        self.df["is_holiday"] = self.df["date"].dt.date.apply(
            lambda d: d in fr_holidays
        )

        print("[INFO] Holiday feature added. Sample:")
        print(self.df.head(2))
        return self

    # -----------------------------------------------------------
    def drop_date_column(self) -> "FeaturesEngineering":
        """
        Drop the original 'date' column from the dataframe.

        Returns:
            self (FeaturesEngineering): method chaining
        """
        print("[STEP] Dropping 'date' column...")

        if "date" in self.df.columns:
            self.df = self.df.drop(columns=["date"])
            print("[INFO] 'date' column dropped.")
        else:
            print("[WARNING] 'date' column was already missing.")

        return self

    # -----------------------------------------------------------
    def save_to_csv(
        self, path: str = OUTPUT_PATH, filename: str = "features_eng_data.csv"
    ) -> None:
        """
        Save final dataframe to CSV.

        Args:
            path (str | Path): directory where file will be saved
            filename (str): name of the output file
        """
        print(f"[STEP] Saving dataframe to CSV: {filename}")
        file_path = path / filename
        self.df.to_csv(file_path, index=False)
        print(f"[INFO] File saved successfully at: {file_path}")

    # -----------------------------------------------------------
    def get_data(self) -> pd.DataFrame:
        """
        Return the final processed dataframe.

        Returns:
            pd.DataFrame: final dataset
        """
        print("[INFO] Returning final processed dataframe. Shape:", self.df.shape)
        return self.df
