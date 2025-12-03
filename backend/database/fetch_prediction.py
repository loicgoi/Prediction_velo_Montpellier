from .database_manager import DatabaseManager
from dotenv import load_dotenv
import os
from database.database import CounterInfo

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def fetch_prediction():
    db = DatabaseManager(DATABASE_URL)

    # Just test the connection and fetch existing rows
    with db.get_session() as session:
        result = session.query(CounterInfo).all()
        for row in result:
            print(row)


if __name__ == "__main__":
    fetch_prediction()
