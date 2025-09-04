"""
API router for job management endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from core.custom_api_route import HandleResponseRoute
from core.dependencies.db import DBSession
from schemas.job import JobCreate, JobRead, JobUpdate, JobOut
from services import job_service
from core.dependencies.aaa import require_permissions
from schemas.account import Permissions
from core.custom_page import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from models.job import Job
from sqlalchemy import select


router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["jobs"]
)


@router.post("/create", response_model=JobRead, status_code=status.HTTP_201_CREATED)
@require_permissions(Permissions.admin)
async def create_job(
    job_data: JobCreate,
    db: DBSession
) -> JobRead:
    """
    Create a new log sending job.
    
    Args:
        job_data: Job creation data
        db: Database session
        
    Returns:
        JobRead: Created job data
    """
    return await job_service.create_job(db, job_data)


@router.get("/list", response_model=Page[JobOut])
@require_permissions(Permissions.admin)
async def get_jobs(
    db: DBSession,
) -> List[JobRead]:
    """
    Get a list of all jobs with pagination.
    
    Args:
        db: Database session
        
    Returns:
        List[JobRead]: List of jobs
    """
    query = select(Job).order_by(Job.created_at.desc())
    return await paginate(db, query)


@router.get("/{job_id}", response_model=JobRead)
@require_permissions(Permissions.admin)
async def get_job(
    job_id: str,
    db: DBSession
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
@require_permissions(Permissions.admin)
async def start_job(
    job_id: str,
    db: DBSession
) -> JobRead:
    """
    Start a job (change status to RUNNING and begin sending logs).
    
    Args:
        job_id: Job str
        db: Database session
        
    Returns:
        JobRead: Updated job data
    """
    job = await job_service.start_job(db, job_id)
    return job

@router.post("/{job_id}/stop", response_model=JobRead)
@require_permissions(Permissions.admin)
async def stop_job(
    job_id: str,
    db: DBSession
) -> JobRead:
    """
    Stop a job (change status to STOPPED).
    
    Args:
        job_id: Job str
        db: Database session
        
    Returns:
        JobRead: Updated job data
    """
    return await job_service.stop_job(db, job_id)


@router.put("/{job_id}", response_model=JobRead)
@require_permissions(Permissions.admin)
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    db: DBSession
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
    return await job_service.update_job(db, job_id, job_data)


@router.delete("/{job_id}")
@require_permissions(Permissions.admin)
async def delete_job(
    job_id: str,
    db: DBSession
) -> None:
    """
    Delete a job.
    
    Args:
        job_id: Job UUID
        db: Database session
        
    Raises:
        HTTPException: If job not found
    """
    deleted = await job_service.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return None