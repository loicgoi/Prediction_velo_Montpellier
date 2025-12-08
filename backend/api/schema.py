from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class CounterDTO(BaseModel):
    """
    Data Transfer Object to send meter information to the frontend.
    """

    model_config = ConfigDict(from_attributes=True)

    station_id: str
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
