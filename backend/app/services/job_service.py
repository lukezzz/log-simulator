"""
Service layer for job management business logic.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
import redis
from models.job import Job, JobStatusEnum
from models.log_template import LogTemplate
from schemas.job import JobCreate, JobUpdate
from core.settings import cfg


# Redis client for sending commands to worker
redis_client = redis.from_url(cfg.REDIS_URI, decode_responses=True)


async def create_job(db: Session, job_data: JobCreate) -> Job:
    """
    Create a new job.
    
    Args:
        db: Database session
        job_data: Job creation data
        
    Returns:
        Job: Created job instance
        
    Raises:
        HTTPException: If template doesn't exist
    """
    # Validate that the template exists
    template_id = str(job_data.template_id)
    statement = select(LogTemplate).where(LogTemplate.id == template_id)
    result = await db.execute(statement)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {job_data.template_id} not found"
        )
    
    # Validate destination (basic validation)
    if not _is_valid_destination(job_data.destination_host, job_data.destination_port):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination host or port"
        )
    
    # Create the job
    db_job = Job(
        template_id=template_id,
        protocol=job_data.protocol,
        destination_host=job_data.destination_host,
        destination_port=job_data.destination_port,
        status=JobStatusEnum.IDLE,
        start_time=job_data.start_time,
        end_time=job_data.end_time,
        send_count=job_data.send_count,
        send_interval_ms=job_data.send_interval_ms
    )
    
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    return db_job


def get_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[Job]:
    """
    Get all jobs with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Job]: List of jobs
    """
    statement = select(Job).offset(skip).limit(limit)
    result = db.execute(statement)
    return result.scalars().all()

async def get_job_by_id(db: Session, job_id: UUID) -> Optional[Job]:
    """
    Get a job by its ID.
    
    Args:
        db: Database session
        job_id: Job UUID
        
    Returns:
        Optional[Job]: Job instance if found, None otherwise
    """
    statement = select(Job).where(Job.id == job_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def start_job(db: Session, job_id: UUID) -> Job:
    """
    Start a job by sending a command to the worker.
    
    Args:
        db: Database session
        job_id: Job UUID
        
    Returns:
        Job: Updated job instance
        
    Raises:
        HTTPException: If job not found or cannot be started
    """
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    
    if job.status not in [JobStatusEnum.IDLE, JobStatusEnum.STOPPED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start job with status {job.status}. Job must be IDLE or STOPPED."
        )
    
    try:
        # Send START command to worker via Redis pub/sub
        redis_client.publish("job_commands", f"START:{job_id}")
        
        # Update status to indicate we've dispatched the start command
        job.status = JobStatusEnum.RUNNING
        db.commit()
        db.refresh(job)
        
        print(f"[REDIS] Sent START command for job {job_id}")
        
    except Exception as e:
        print(f"[ERROR] Failed to send START command for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start job - worker communication error"
        )
    
    return job


async def stop_job(db: Session, job_id: str) -> Job:
    """
    Stop a job by sending a command to the worker.
    
    Args:
        db: Database session
        job_id: Job str
        
    Returns:
        Job: Updated job instance
        
    Raises:
        HTTPException: If job not found or cannot be stopped
    """
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    
    if job.status != JobStatusEnum.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot stop job with status {job.status}. Job must be RUNNING."
        )
    
    try:
        # Send STOP command to worker via Redis pub/sub
        redis_client.publish("job_commands", f"STOP:{job_id}")
        
        # Update status to indicate we've dispatched the stop command  
        job.status = JobStatusEnum.STOPPED
        db.commit()
        db.refresh(job)
        
        print(f"[REDIS] Sent STOP command for job {job_id}")
        
    except Exception as e:
        print(f"[ERROR] Failed to send STOP command for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop job - worker communication error"
        )
    
    return job


async def update_job(db: Session, job_id: UUID, job_data: JobUpdate) -> Job:
    """
    Update a job.
    
    Args:
        db: Database session
        job_id: Job UUID
        job_data: Job update data
        
    Returns:
        Job: Updated job instance
        
    Raises:
        HTTPException: If job not found or update is invalid
    """
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    
    # Update only provided fields
    for field, value in job_data.model_dump(exclude_unset=True).items():
        if field == "template_id" and value:
            # Validate template exists
            statement = select(LogTemplate).where(LogTemplate.id == value)
            result = db.execute(statement)
            template = result.scalar_one_or_none()
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Template with id {value} not found"
                )
        
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)

    return job


async def delete_job(db: Session, job_id: UUID) -> bool:
    """
    Delete a job.
    
    Args:
        db: Database session
        job_id: Job UUID
        
    Returns:
        bool: True if job was deleted, False if not found
    """
    job = await get_job_by_id(db, job_id)
    if not job:
        return False
    
    await db.delete(job)
    await db.commit()
    
    return True


def _is_valid_destination(host: str, port: int) -> bool:
    """
    Basic validation for destination host and port.
    
    Args:
        host: Destination hostname or IP
        port: Destination port
        
    Returns:
        bool: True if destination appears valid
    """
    # Basic validation - in production, you might want more sophisticated checks
    if not host or not host.strip():
        return False
    
    if port < 1 or port > 65535:
        return False
    
    return True