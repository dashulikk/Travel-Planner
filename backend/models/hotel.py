from pydantic import BaseModel, Field
from datetime import date, datetime

# Готелі
class HotelCreate(BaseModel):
    name: str = Field(..., example="Hilton Paris Opera")
    check_in: date
    check_out: date
    estimated_cost: float = Field(default=0.0, example=400.0)

# Транспорт
class TransportCreate(BaseModel):
    type: str = Field(..., example="flight")  # flight або train
    company: str = Field(..., example="Air France")
    departure_city: str = Field(..., example="Kyiv")
    arrival_city: str = Field(..., example="Paris")
    departure_time: datetime
    arrival_time: datetime
    estimated_cost: float = Field(default=0.0, example=200.0)
