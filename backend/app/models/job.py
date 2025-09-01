"""
Job model for managing log sending jobs.
"""
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.db.base import BaseModel


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
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("log_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to log template"
    )
    
    # Network protocol to use
    protocol = Column(
        Enum(ProtocolEnum),
        nullable=False,
        comment="Network protocol (TCP or UDP)"
    )
    
    # Destination configuration
    destination_host = Column(
        String(255),
        nullable=False,
        comment="Target host IP address or hostname"
    )
    
    destination_port = Column(
        Integer,
        nullable=False,
        comment="Target port number"
    )
    
    # Job status
    status = Column(
        Enum(JobStatusEnum),
        nullable=False,
        default=JobStatusEnum.IDLE,
        index=True,
        comment="Current job status"
    )
    
    # Scheduling fields
    start_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled start time for the job"
    )
    
    end_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled end time for the job"
    )
    
    send_count = Column(
        Integer,
        nullable=True,
        comment="Total number of logs to send (null for unlimited)"
    )
    
    send_interval_ms = Column(
        Integer,
        nullable=True,
        default=1000,
        comment="Delay in milliseconds between each log sent"
    )
    
    # Relationship to log template
    template = relationship(
        "LogTemplate",
        back_populates="jobs"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Job(id={self.id}, template_id={self.template_id}, "
            f"protocol={self.protocol}, destination={self.destination_host}:{self.destination_port}, "
            f"status={self.status})>"
        )