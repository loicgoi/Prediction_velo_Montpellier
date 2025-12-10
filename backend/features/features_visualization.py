import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import holidays
from utils.paths import OUTPUT_PATH

# Display settings
sns.set_context("notebook", font_scale=1.0)
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12


class FeaturesVisualization:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with dataset.
        df: DataFrame with columns: station_id, date, intensity, latitude, longitude, avg_temp, precipitation, vent_max
        """
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        # Detect French holidays based on the year range in the data
        years = self.df["date"].dt.year.unique()
        year_range = range(min(years), max(years) + 2)
        fr_holidays = holidays.FR(years=year_range)
        self.holidays = fr_holidays

        self._add_features()
        self.max_intensity = self.df["intensity"].max() * 1.05

    def _add_features(self):
        """Create new features for plotting"""
        self.df["weekday"] = self.df["date"].dt.day_name()
        self.df["is_weekend"] = self.df["date"].dt.weekday >= 5
        self.df["is_holiday"] = self.df["date"].dt.date.isin(self.holidays)

        self.df["month"] = self.df["date"].dt.month
        self.df["season"] = self.df["month"].map(
            {
                12: "Winter",
                1: "Winter",
                2: "Winter",
                3: "Spring",
                4: "Spring",
                5: "Spring",
                6: "Summer",
                7: "Summer",
                8: "Summer",
                9: "Fall",
                10: "Fall",
                11: "Fall",
            }
        )
        self.df["temp_category"] = pd.cut(
            self.df["avg_temp"],
            bins=[-100, 10, 20, 100],
            labels=["Cold", "Mild", "Hot"],
        )
        self.df["rainy"] = self.df["precipitation_mm"] > 0
        self.df["windy"] = self.df["vent_max"] > 15

    def _set_custom_yticks(self, ax):
        """
        Helper function to set custom Y-axis ticks with SMALLER FONT SIZE:
        0, 100, 200... 1000, then 2000, 3000...
        """
        # Part 1: From 0 to 1000 with step 100
        ticks_detailed = list(range(0, 1001, 100))

        # Part 2: From 2000 to max value with step 1000
        max_val = int(self.max_intensity)
        if max_val > 1000:
            ticks_large = list(range(2000, max_val + 2000, 1000))
        else:
            ticks_large = []

        # Combine lists
        all_ticks = ticks_detailed + ticks_large

        # Filter ticks that are way beyond the max intensity to keep plot clean
        all_ticks = [t for t in all_ticks if t <= self.max_intensity + 500]

        ax.set_yticks(all_ticks)

        # KEY CHANGE: Reduce the font size of Y-axis labels to prevent overlapping
        ax.tick_params(axis="y", labelsize=8)

    def plot_temporal_features(self):
        """Plot intensity vs temporal features (Grid 2x2)"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()

        # 1. Day of week
        sns.boxplot(
            x="weekday",
            y="intensity",
            data=self.df,
            order=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            ax=axes[0],
        )
        axes[0].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[0])  # Apply custom ticks & size
        axes[0].set_title("Day of Week")
        axes[0].set_xlabel("")
        axes[0].tick_params(axis="x", rotation=30)

        # 2. Weekend
        sns.boxplot(x="is_weekend", y="intensity", data=self.df, ax=axes[1])
        axes[1].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[1])  # Apply custom ticks & size
        axes[1].set_title("Weekend Effect")
        axes[1].set_xlabel("")

        # 3. Holidays
        sns.boxplot(x="is_holiday", y="intensity", data=self.df, ax=axes[2])
        axes[2].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[2])  # Apply custom ticks & size
        axes[2].set_title("Holiday Effect (France)")
        axes[2].set_xlabel("Is Holiday?")

        # 4. Season
        sns.boxplot(
            x="season",
            y="intensity",
            data=self.df,
            order=["Winter", "Spring", "Summer", "Fall"],
            ax=axes[3],
        )
        axes[3].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[3])  # Apply custom ticks & size
        axes[3].set_title("Season Effect")
        axes[3].set_xlabel("")

        plt.tight_layout()
        plt.show()

    def plot_weather_features(self):
        """Plot intensity vs weather features (Horizontal 1x3)"""
        fig, axes = plt.subplots(1, 3, figsize=(16, 6))

        # Temperature
        sns.boxplot(x="temp_category", y="intensity", data=self.df, ax=axes[0])
        axes[0].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[0])  # Apply custom ticks & size
        axes[0].set_title("Temperature")
        axes[0].set_xlabel("")

        # Precipitation
        sns.boxplot(x="rainy", y="intensity", data=self.df, ax=axes[1])
        axes[1].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[1])  # Apply custom ticks & size
        axes[1].set_title("Precipitation (Rain)")
        axes[1].set_xlabel("")

        # Wind
        sns.boxplot(x="windy", y="intensity", data=self.df, ax=axes[2])
        axes[2].set_ylim(0, self.max_intensity)
        self._set_custom_yticks(axes[2])  # Apply custom ticks & size
        axes[2].set_title("Wind (>15 km/h)")
        axes[2].set_xlabel("")

        plt.tight_layout()
        plt.show()

    def plot_spatial_features(self):
        """Plot spatial effect (Map) - No custom Y-ticks needed for Latitude"""
        plt.figure(figsize=(12, 8))
        sns.scatterplot(
            x="longitude",
            y="latitude",
            size="intensity",
            hue="intensity",
            data=self.df,
            sizes=(30, 300),
            palette="viridis",
            alpha=0.7,
        )
        plt.title("Spatial Intensity Map")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.show()

    def plot_station_effect(self):
        """Plot intensity per station"""
        plt.figure(figsize=(14, 6))
        ax = sns.boxplot(x="station_id", y="intensity", data=self.df)
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.ylim(0, self.max_intensity)
        self._set_custom_yticks(ax)  # Apply custom ticks & size
        plt.title("Station Intensity Distribution")
        plt.tight_layout()
        plt.show()

    def plot_correlation_heatmap(self):
        """Plot correlation heatmap"""
        numeric_cols = ["intensity", "avg_temp", "precipitation_mm", "vent_max"]
        corr = self.df[numeric_cols].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title("Feature Correlation")
        plt.show()

    def show_all_plots(self):
        """Display all plots"""
        self.plot_temporal_features()
        self.plot_weather_features()
        self.plot_spatial_features()
        self.plot_station_effect()
        self.plot_correlation_heatmap()


if __name__ == "__main__":
    # Load your dataset here
    df = pd.read_csv(OUTPUT_PATH / "dataset_final.csv")

    viz = FeaturesVisualization(df)
    viz.show_all_plots()
