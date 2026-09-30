from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from auth.jwt import authenticate_user, get_password_hash, create_access_token
from config.database import db_dependency
from schemas.user import TokenResponse, UserCreate, UserResponse
from models.user import User
from starlette import status
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(db: db_dependency, user: UserCreate):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    new_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=TokenResponse)
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=EXPIRE_MINUTES))

    return {
        "access_token": token,
        "token_type": "bearer"
    }
