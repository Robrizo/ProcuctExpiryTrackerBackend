from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
import uuid

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=120)
    last_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("user", max_length=50)

class UserUpdate(BaseModel):
    username: str = Field(None, min_length=2, max_length=50)
    first_name: str = Field(None, min_length=2, max_length=120)
    last_name: str = Field(None, min_length=2, max_length=120)
    email: EmailStr = Field(None)
    role: str = Field(None, max_length=50)
    password: str = Field(None, min_length=6, max_length=100)

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
