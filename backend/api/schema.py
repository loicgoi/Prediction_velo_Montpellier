from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class CounterDTO(BaseModel):
    """
    Data Transfer Object to send meter information to the frontend.
    """

    station_id: str
    name: Optional[str] = None  # This is where the frontend will read the street name.
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True  # Allows you to convert the SQLAlchemy object directly
