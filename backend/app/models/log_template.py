"""
LogTemplate model for storing log templates.
"""
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .job import Job


class LogTemplate(BaseModel):
    """
    Model for log templates that define the structure and content of logs.
    
    A template contains the pattern/format for generating log messages.
    """
    
    __tablename__ = "log_templates"
    
    name: Mapped[str] = mapped_column(
        String(255), 
        unique=True,
        index=True,
        comment="Unique, human-readable name for the template"
    )
    device_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
        comment="Device type for categorizing the template (e.g., 'FortiGate')"
    )
    content_format: Mapped[str] = mapped_column(
        Text,
        comment="The log format string for this template"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Optional description providing more context for the template"
    )
    is_predefined: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Flag to distinguish between system-provided and user-custom templates"
    )
    
    # Relationship to jobs
    jobs: Mapped[List["Job"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the LogTemplate."""
        return (
            f"LogTemplate(id={self.id!r}, name={self.name!r}, "
            f"device_type={self.device_type!r}, is_predefined={self.is_predefined}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the LogTemplate."""
        return f"LogTemplate '{self.name}' ({self.device_type})"
    
