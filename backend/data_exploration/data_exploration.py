class Statistics:
    def __init__(self, df):
        self.df = df

    def info(self):
        print("\n--- DataFrame Info ---")
        self.df.info()
        print("----------------------\n")

    def describe(self):
        print("\n--- DataFrame Description (describe) ---")
        result = self.df.describe()
        print(result)
        print("----------------------------------------\n")
        return result

    def isna(self):
        print("\n--- Missing Values (isna) ---")
        result = self.df.isna().sum()
        print(result)
        print("-----------------------------\n")
        return result

    def duplicated(self):
        print("\n--- Duplicated Rows ---")
        result = self.df.duplicated().sum()
        print(f"Number of duplicated rows: {result}")
        print("----------------------\n")
        return result

    # def outliers_rolling(self, column="value", window=5, std_factor=3):
    #     """Detect anomalies compared to rolling mean."""
    #     print(
    #         f"\n--- Rolling-Window Outliers (column='{column}', window={window}, std_factor={std_factor}) ---"
    #     )
    #     rolling_mean = self.df[column].rolling(window).mean()
    #     rolling_std = self.df[column].rolling(window).std()

    #     upper = rolling_mean + std_factor * rolling_std
    #     lower = rolling_mean - std_factor * rolling_std

    #     outliers = self.df[(self.df[column] > upper) | (self.df[column] < lower)]

    #     print(f"Found {len(outliers)} outliers:")
    #     if not outliers.empty:
    #         print(outliers)
    #     else:
    #         print("No outliers found.")
    #     print("------------------------------------------------------\n")
    #     return outliers
