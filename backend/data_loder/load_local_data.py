from pathlib import Path
import pandas as pd


def load_local_data(folder_path):
    dfs = {}
    DATA_FOLDER = Path(folder_path)  # use the folder_path passed to the function
    files = list(DATA_FOLDER.glob("*.[cC][sS][vV]"))
    if not files:
        print(f"No CSV files found in {DATA_FOLDER.resolve()}")
        return dfs

    for file in files:
        name = file.stem
        dfs[name] = pd.read_csv(file)
        print(f"Loaded {name}.csv from {DATA_FOLDER.resolve()}")
    return dfs
