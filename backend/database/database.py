from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Numeric,
    create_engine,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
Base = declarative_base()


class CounterInfo(Base):
    """Table for all counter information"""

    __tablename__ = "counters_info"

    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    longitude = Column(Numeric(9, 6))
    latitude = Column(Numeric(8, 6))


class BikeCount(Base):
    """Table for bike counting data"""

    __tablename__ = "bike_count"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    counter_id = Column(
        String(255), ForeignKey("counters_info.id"), nullable=False, index=True
    )
    intensity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Prediction(Base):
    """Table for predictions"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_date = Column(DateTime, nullable=False, index=True)
    counter_id = Column(
        String(255), ForeignKey("counters_info.id"), nullable=False, index=True
    )
    prediction_value = Column(Integer, nullable=False)
    model_version = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class Weather(Base):
    """Table for weather data"""

    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    avg_temp = Column(Float(2), nullable=False)
    precipitation_mm = Column(Float)
    vent_max = Column(Float)


class ModelMetrics(Base):
    """Table for model metrics"""

    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter_id = Column(
        String(255), ForeignKey("counters_info.id"), nullable=False, index=True
    )
    date = Column(DateTime, nullable=False, index=True)
    actual_value = Column(Integer)
    predicted_value = Column(Integer)
    absolute_error = Column(Float)
    mean_absolute_error = Column(Float)
    model_version = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class DatabaseManager:
    """Gestionnaire de base de données"""

    def __init__(self, database_url: str = None):
        database_url = database_url or os.getenv(
            "DATABASE_URL", "sqlite:///./bike_count_montpellier.db"
        )
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()

    def _setup_engine(self):
        """Configure the database engine"""
        try:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False}
                if "sqlite" in self.database_url
                else {},
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info(f"Database engine configure from: {self.database_url}")
        except Exception as e:
            logger.error(f"Error setting up database engine: {e}")
            raise

    def init_db(self):
        """Initialises the database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Databse tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_session(self):
        """Returns a database session"""
        return self.SessionLocal()


db_manager = DatabaseManager()
