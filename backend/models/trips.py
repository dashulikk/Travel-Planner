from pydantic import BaseModel, Field
from datetime import date


class TripCreate(BaseModel):
    name: str = Field(..., example="Trip to Paris")
    city: str = Field(..., example="Paris")
    country: str = Field(..., example="France")
    start_date: date
    end_date: date

# Модель відповіді для подорожі
class TripResponse(BaseModel):
    id: int
    user_id: int
    name: str
    city: str
    country: str
    start_date: date
    end_date: date
    reference_id: str

    class Config:
        orm_mode = True
