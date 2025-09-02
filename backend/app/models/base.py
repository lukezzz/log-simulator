"""
Database base model and shared functionality.
"""
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from core.security import gen_uuid


class BaseModel(DeclarativeBase):
    """Base model with common fields for all entities."""
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(primary_key=True, default=gen_uuid)

    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )