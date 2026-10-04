import uuid
from datetime import datetime, timezone

from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        String, Text, Uuid)
from sqlalchemy.orm import relationship

from app.config.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid7, unique=True, nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(80), nullable=False, default="General")
    quantity = Column(Integer, nullable=False, default=1)
    purchase_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", back_populates="products")