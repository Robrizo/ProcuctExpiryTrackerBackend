from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, Uuid, String, DateTime, Uuid
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), default=uuid.uuid7, unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.datetime.now(timezone.utc), 
        onupdate=datetime.datetime.now(timezone.utc), 
        nullable=False
        )
    
    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")