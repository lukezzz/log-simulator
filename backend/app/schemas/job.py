"""
Pydantic schemas for Job API endpoints.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from models.job import ProtocolEnum, JobStatusEnum


class JobBase(BaseModel):
    """Base schema with common job fields."""
    
    template_id: UUID = Field(
        ...,
        description="ID of the log template to use"
    )
    protocol: ProtocolEnum = Field(
        ...,
        description="Network protocol (TCP or UDP)"
    )
    destination_host: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Target host IP address or hostname"
    )
    destination_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="Target port number (1-65535)"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Scheduled start time for the job"
    )
    end_time: Optional[datetime] = Field(
        None,
        description="Scheduled end time for the job"
    )
    send_count: Optional[int] = Field(
        None,
        ge=1,
        description="Total number of logs to send (null for unlimited)"
    )
    send_interval_ms: Optional[int] = Field(
        1000,
        ge=1,
        description="Delay in milliseconds between each log sent"
    )


class JobCreate(JobBase):
    """Schema for creating a new job."""
    pass


class JobUpdate(BaseModel):
    """Schema for updating an existing job."""
    
    template_id: Optional[UUID] = Field(
        None,
        description="ID of the log template to use"
    )
    protocol: Optional[ProtocolEnum] = Field(
        None,
        description="Network protocol (TCP or UDP)"
    )
    destination_host: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Target host IP address or hostname"
    )
    destination_port: Optional[int] = Field(
        None,
        ge=1,
        le=65535,
        description="Target port number (1-65535)"
    )
    status: Optional[JobStatusEnum] = Field(
        None,
        description="Job status"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Scheduled start time for the job"
    )
    end_time: Optional[datetime] = Field(
        None,
        description="Scheduled end time for the job"
    )
    send_count: Optional[int] = Field(
        None,
        ge=1,
        description="Total number of logs to send (null for unlimited)"
    )
    send_interval_ms: Optional[int] = Field(
        None,
        ge=1,
        description="Delay in milliseconds between each log sent"
    )


class JobRead(JobBase):
    """Schema for reading job data from API responses."""
    
    id: UUID = Field(
        ...,
        description="Unique job identifier"
    )
    status: JobStatusEnum = Field(
        ...,
        description="Current job status"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when job was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when job was last updated"
    )
    
    class Config:
        from_attributes = True


class JobStatusUpdate(BaseModel):
    """Schema for updating only job status."""
    
    status: JobStatusEnum = Field(
        ...,
        description="New job status"
    )