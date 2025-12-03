from pathlib import Path

# Base paths
BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / ".." / "data"

# Archive path
ARCHIVE_PATH = DATA_PATH / "archive"
ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)

# Output path for clean data
OUTPUT_PATH = DATA_PATH / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Output path for trained model
MODELS_PATH = DATA_PATH / "models"
MODELS_PATH.mkdir(parents=True, exist_ok=True)
