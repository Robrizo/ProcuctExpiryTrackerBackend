from datetime import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: str = Field("General", max_length=80)
    quantity: int = Field(..., ge=1)
    purchase_date: datetime.date
    expiry_date: datetime.date
    notes: Optional[str]  = None

class ProductCreate(ProductBase):
    pass