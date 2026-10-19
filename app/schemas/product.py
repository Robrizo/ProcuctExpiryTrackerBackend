from datetime import date, datetime
import uuid
from typing import Optional

from psycopg import Date
from pydantic import BaseModel, Field, field_validator

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    category: str = Field("General", max_length=80)
    quantity: int = Field(..., ge=1)
    purchase_date: date
    expiry_date: date 
    notes: str | None = Field(default=None, max_length=500)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    category: Optional[str] = Field(None, max_length=80)
    quantity: Optional[int] = Field(None, ge=1)
    purchase_date: Optional[date]
    expiry_date: Optional[date]
    notes: Optional[str] = Field(default=None, min_length=3, max_length=500)

class ProductResponse(ProductBase):
    id: uuid.UUID
    user_id: uuid.UUID
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
    status: str
    days_until_expiry: int

    class Config:
        from_attributes = True