import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette import status

from app.models.user import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='api/auth/login')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(username: str, user_id: uuid.UUID, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": str(user_id), "role": role, "type": "access"}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str, user_id: uuid.UUID, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": str(user_id), "role": role, "type": "refresh"}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to validate user")

def verify_refresh_token(token: str):
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    username: str = payload.get("sub")
    user_id: str = payload.get("id")
    user_role: str = payload.get("role")

    if username is None or user_id is None or user_role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to validate user")

    try:
        user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID")

    return {
        "username": username,
        "user_id": user_id,
        "user_role": user_role
    }

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to validate user")
        
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID")
        
        return {
            "username": username,
            "user_id": user_id,
            "user_role": user_role
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to validate user")

user_dependancy = Annotated[dict, Depends(get_current_user)]
