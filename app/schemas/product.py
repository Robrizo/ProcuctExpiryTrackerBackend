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
    notes: str | None = Field(default=None, min_length=3, max_length=500)

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, value: date):
        if value <= date.today():
            raise ValueError("Expiry date must be in the future")
        return value

    @field_validator("purchase_date")
    @classmethod
    def validate_purchase_date(cls, value: date):
        if value > date.today():
            raise ValueError("Purchase date cannot be in the future")
        return value

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: uuid.UUID
    user_id: uuid.UUID
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
    status: Optional[str] | None
    days_until_expiry: Optional[int] | None

    class Config:
        from_attributes = True