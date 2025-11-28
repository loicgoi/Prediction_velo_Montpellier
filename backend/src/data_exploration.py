import pandas as pd
from typing import Union, List


class Statistics:
    """
    A class to perform basic data exploration on one or more pandas DataFrames.
    """

    def __init__(
        self,
        dataframes: Union[pd.DataFrame, List[pd.DataFrame]],
        names: Union[str, List[str]] = None,
    ):
        """
        Initialize with one or more DataFrames.

        Args:
            dataframes (pd.DataFrame or List[pd.DataFrame]): DataFrame(s) to analyze.
            names (str or List[str], optional): Name(s) of the DataFrame(s) for printing purposes.
        """
        if isinstance(dataframes, pd.DataFrame):
            self.dataframes = [dataframes]
        else:
            self.dataframes = dataframes

        if names is None:
            self.names = [f"DataFrame {i + 1}" for i in range(len(self.dataframes))]
        elif isinstance(names, str):
            self.names = [names]
        else:
            self.names = names

    def info(self):
        """Print info for all DataFrames."""
        for df, name in zip(self.dataframes, self.names):
            print(f"\n--- {name} Info ---")
            df.info()
            print("----------------------\n")

    def describe(self):
        """Print describe() for all DataFrames."""
        results = []
        for df, name in zip(self.dataframes, self.names):
            print(f"\n--- {name} Description (describe) ---")
            result = df.describe()
            print(result)
            print("----------------------------------------\n")
            results.append(result)
        return results

    def isna(self):
        """Print missing values for all DataFrames."""
        results = []
        for df, name in zip(self.dataframes, self.names):
            print(f"\n--- {name} Missing Values (isna) ---")
            result = df.isna().sum()
            print(result)
            print("-----------------------------\n")
            results.append(result)
        return results

    def duplicated(self):
        """Print duplicated rows for all DataFrames."""
        results = []
        for df, name in zip(self.dataframes, self.names):
            print(f"\n--- {name} Duplicated Rows ---")
            result = df.duplicated().sum()
            print(f"Number of duplicated rows: {result}")
            print("----------------------\n")
            results.append(result)
        return results
