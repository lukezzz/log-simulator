"""
Pydantic schemas for LogTemplate API endpoints.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class LogTemplateCreate(BaseModel):
    """Schema for creating a new log template."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique, human-readable name for the template"
    )
    device_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Device type for categorizing the template (e.g., 'FortiGate')"
    )
    content_format: str = Field(
        ...,
        min_length=1,
        description="The log format string for this template"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description providing more context for the template"
    )
    is_predefined: bool = Field(
        False,
        description="Flag to distinguish between system-provided and user-custom templates"
    )


class LogTemplateRead(BaseModel):
    """Schema for reading template data from API responses."""
    
    id: UUID = Field(
        ...,
        description="Unique template identifier"
    )
    name: str = Field(
        ...,
        description="Template name"
    )
    device_type: str = Field(
        ...,
        description="Device type"
    )
    content_format: str = Field(
        ...,
        description="Log format string"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description providing more context for the template"
    )
    is_predefined: bool = Field(
        ...,
        description="Flag to distinguish between system-provided and user-custom templates"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when template was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when template was last updated"
    )
    
    class Config:
        from_attributes = True


class LogTemplateUpdate(BaseModel):
    """Schema for updating an existing log template."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Unique, human-readable name for the template"
    )
    device_type: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Device type for categorizing the template (e.g., 'FortiGate')"
    )
    content_format: Optional[str] = Field(
        None,
        min_length=1,
        description="The log format string for this template"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description providing more context for the template"
    )