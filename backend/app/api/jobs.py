"""
API router for job management endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.db.session import get_db
from schemas.job import JobCreate, JobRead, JobUpdate
from services import job_service


router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"]
)


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
) -> JobRead:
    """
    Create a new log sending job.
    
    Args:
        job_data: Job creation data
        db: Database session
        
    Returns:
        JobRead: Created job data
    """
    job = job_service.create_job(db, job_data)
    return JobRead.model_validate(job)


@router.get("/", response_model=List[JobRead])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[JobRead]:
    """
    Get a list of all jobs with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[JobRead]: List of jobs
    """
    jobs = job_service.get_jobs(db, skip=skip, limit=limit)
    return [JobRead.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> JobRead:
    """
    Get a specific job by ID.
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Returns:
        JobRead: Job data
        
    Raises:
        HTTPException: If job not found
    """
    job = job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return JobRead.model_validate(job)


@router.post("/{job_id}/start", response_model=JobRead)
def start_job(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> JobRead:
    """
    Start a job (change status to RUNNING and begin sending logs).
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Returns:
        JobRead: Updated job data
    """
    job = job_service.start_job(db, job_id)
    return JobRead.model_validate(job)


@router.post("/{job_id}/stop", response_model=JobRead)
def stop_job(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> JobRead:
    """
    Stop a job (change status to STOPPED).
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Returns:
        JobRead: Updated job data
    """
    job = job_service.stop_job(db, job_id)
    return JobRead.model_validate(job)


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: Session = Depends(get_db)
) -> JobRead:
    """
    Update a job.
    
    Args:
        job_id: Job UUID
        job_data: Job update data
        db: Database session
        
    Returns:
        JobRead: Updated job data
    """
    job = job_service.update_job(db, job_id, job_data)
    return JobRead.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a job.
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Raises:
        HTTPException: If job not found
    """
    deleted = job_service.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )