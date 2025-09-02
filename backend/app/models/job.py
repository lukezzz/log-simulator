"""
Job model for managing log sending jobs.
"""
import enum
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .log_template import LogTemplate


class ProtocolEnum(str, enum.Enum):
    """Enum for supported network protocols."""
    TCP = "TCP"
    UDP = "UDP"


class JobStatusEnum(str, enum.Enum):
    """Enum for job status values."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class Job(BaseModel):
    """
    Model for log sending jobs.
    
    A job defines the configuration for sending logs from a template
    to a specific network destination using a specified protocol.
    """
    
    __tablename__ = "jobs"
    
    # Reference to the log template to use
    template_id: Mapped[str] = mapped_column(String(64), ForeignKey("log_templates.id"))

    # Network protocol to use
    protocol: Mapped[ProtocolEnum] = mapped_column(
        Enum(ProtocolEnum),
        comment="Network protocol (TCP or UDP)"
    )
    
    # Destination configuration
    destination_host: Mapped[str] = mapped_column(
        String(255),
        comment="Target host IP address or hostname"
    )
    
    destination_port: Mapped[int] = mapped_column(
        Integer,
        comment="Target port number"
    )
    
    # Job status
    status: Mapped[JobStatusEnum] = mapped_column(
        Enum(JobStatusEnum),
        default=JobStatusEnum.IDLE,
        index=True,
        comment="Current job status"
    )
    
    # Scheduling fields
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Scheduled start time for the job"
    )
    
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Scheduled end time for the job"
    )
    
    send_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Total number of logs to send (null for unlimited)"
    )
    
    send_interval_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=1000,
        comment="Delay in milliseconds between each log sent"
    )
    
    # Relationship to log template
    template: Mapped["LogTemplate"] = relationship(
        back_populates="jobs"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Job(id={self.id}, template_id={self.template_id}, "
            f"protocol={self.protocol}, destination={self.destination_host}:{self.destination_port}, "
            f"status={self.status})>"
        )
    
    def __repr__(self) -> str:
        return (
            f"<Job(id={self.id}, template_id={self.template_id}, "
            f"protocol={self.protocol}, destination={self.destination_host}:{self.destination_port}, "
            f"status={self.status})>"
        )