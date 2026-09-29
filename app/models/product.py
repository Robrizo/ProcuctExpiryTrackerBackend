from datetime import datetime, timezone
from tkinter import Text
import uuid
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Uuid, String, DateTime, Uuid
from sqlalchemy.orm import relationship
from app.config.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid(as_uuid=True), default=uuid.uuid7, unique=True, nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(80), nullable=False, default="General")
    quantity = Column(Integer, nullable=False, default=1)
    purchase_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(timezone.utc),
        onupdate=datetime.datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", back_populates="products")