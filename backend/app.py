from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from models.users import UserRegister, UserLogin
from models.trips import TripCreate
from models.checklist import ChecklistCreate, ChecklistUpdate
from models.hotel import HotelCreate
from models.transport import TransportCreate
from authentication import register_user, authenticate_user
from database import Database

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()
db = Database()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --------------------- Реєстрація та авторизація ---------------------

@app.post("/users/register", tags=["Users"])
def register(user: UserRegister):
    return register_user(user.username, user.email, user.password)


@app.post("/users/login", tags=["Users"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Авторизація користувача та повернення JWT токена.
    Використовує функцію authenticate_user з authentication.py.
    """
    try:
        # Виклик функції з authentication.py
        result = authenticate_user(form_data.username, form_data.password)
        return result
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


# --------------------- Подорожі ---------------------

@app.post("/trips/create", tags=["Trips"])
def create_trip(trip: TripCreate, current_user: str = Depends(get_current_user)):
    """
    Створення нової подорожі для авторизованого користувача.
    """
    user = db.get_user_by_email(current_user)
    trip_id, reference_id = db.create_trip(
        user['id'], trip.name, trip.city, trip.country, trip.start_date, trip.end_date
    )
    return {"message": "Trip created successfully", "trip_id": trip_id, "reference_id": reference_id}

# --------------------- Чек-лист ---------------------

@app.post("/trips/{trip_id}/checklist", tags=["Checklist"])
def add_checklist_item(trip_id: int, item: ChecklistCreate, current_user: str = Depends(get_current_user)):
    """
    Додавання завдання у чек-лист подорожі.
    """
    checklist_id = db.add_checklist_item(trip_id, item.description, item.estimated_cost)
    return {"message": "Checklist item added", "checklist_id": checklist_id}

@app.put("/checklist/{item_id}", tags=["Checklist"])
def update_checklist_item(item_id: int, update: ChecklistUpdate, current_user: str = Depends(get_current_user)):
    """
    Оновлення статусу завдання у чек-листі.
    """
    db.update_checklist_item(item_id, update.is_completed)
    return {"message": "Checklist item updated"}

# --------------------- Готелі ---------------------

@app.post("/trips/{trip_id}/hotels", tags=["Hotels"])
def add_hotel(trip_id: int, hotel: HotelCreate, current_user: str = Depends(get_current_user)):
    """
    Додавання готелю до подорожі.
    """
    hotel_id = db.add_hotel(trip_id, hotel.name, hotel.check_in, hotel.check_out, hotel.estimated_cost)
    return {"message": "Hotel added successfully", "hotel_id": hotel_id}

# --------------------- Транспорт ---------------------

@app.post("/trips/{trip_id}/transport", tags=["Transport"])
def add_transport(trip_id: int, transport: TransportCreate, current_user: str = Depends(get_current_user)):
    """
    Додавання транспорту до подорожі.
    """
    transport_id = db.add_transport(
        trip_id, transport.type, transport.company, transport.departure_city,
        transport.arrival_city, transport.departure_time, transport.arrival_time, transport.estimated_cost
    )
    return {"message": "Transport added successfully", "transport_id": transport_id}
