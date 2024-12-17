from pydantic import BaseModel, Field

# Модель для додавання завдання у чек-лист
class ChecklistCreate(BaseModel):
    description: str = Field(..., example="Book flight tickets")
    estimated_cost: float = Field(default=0.0, example=150.0)

# Модель оновлення статусу завдання
class ChecklistUpdate(BaseModel):
    is_completed: bool = Field(..., example=True)
