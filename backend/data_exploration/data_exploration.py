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