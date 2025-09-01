"""
LogTemplate model for storing log templates.
"""
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from core.db.base import BaseModel


class LogTemplate(BaseModel):
    """
    Model for log templates that define the structure and content of logs.
    
    A template contains the pattern/format for generating log messages.
    """
    
    __tablename__ = "log_templates"
    
    name = Column(
        String(255), 
        nullable=False, 
        unique=True,
        index=True,
        comment="Unique, human-readable name for the template"
    )
    device_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Device type for categorizing the template (e.g., 'FortiGate')"
    )
    content_format = Column(
        Text,
        nullable=False,
        comment="The log format string for this template"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Optional description providing more context for the template"
    )
    is_predefined = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Flag to distinguish between system-provided and user-custom templates"
    )
    
    # Relationship to jobs
    jobs = relationship(
        "Job",
        back_populates="template",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<LogTemplate(id={self.id}, name='{self.name}', device_type='{self.device_type}')>"