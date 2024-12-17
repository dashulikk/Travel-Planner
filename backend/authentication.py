from fastapi import HTTPException, status
from database import Database
from salted_password import SaltedPassword
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
db = Database()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_user(username: str, email: str, password: str):
    existing_user = db.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    salted_password = SaltedPassword(password)
    try:
        user_id = db.add_user(username, email, salted_password.password_hash, salted_password.salt)
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )


def authenticate_user(email: str, password: str):
    """
    Перевіряє користувача та генерує JWT токен.
    """
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    is_valid = SaltedPassword.check_password(password, user['password_hash'], user['salt'])
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
