from dotenv import load_dotenv
import os
from database.database import DatabaseManager, CounterInfo

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a single instance of DatabaseManager
db_manager = DatabaseManager(DATABASE_URL)


def get_db_session():
    """
    FastAPI dependency for obtaining a database session.
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def fetch_prediction():
    # Test the connection and fetch existing rows
    session_gen = get_db_session()
    session = next(session_gen)
    try:
        result = session.query(CounterInfo).all()
        for row in result:
            print(row)
    finally:
        session_gen.close()


if __name__ == "__main__":
    fetch_prediction()
