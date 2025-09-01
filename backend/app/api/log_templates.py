"""
API router for template management endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from core.db.session import get_db
from schemas.log_template import LogTemplateCreate, LogTemplateRead, LogTemplateUpdate
from services import log_template_service


router = APIRouter(
    prefix="/api/v1/templates",
    tags=["templates"]
)


@router.post("/", response_model=LogTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: LogTemplateCreate,
    db: Session = Depends(get_db)
) -> LogTemplateRead:
    """
    Create a new log template.
    
    Args:
        template_data: Template creation data
        db: Database session
        
    Returns:
        LogTemplateRead: Created template data
    """
    template = log_template_service.create_template(db, template_data)
    return LogTemplateRead.model_validate(template)


@router.get("/", response_model=List[LogTemplateRead])
def get_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[LogTemplateRead]:
    """
    Get a list of all templates with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[LogTemplateRead]: List of templates
    """
    templates = log_template_service.get_templates(db, skip=skip, limit=limit)
    return [LogTemplateRead.model_validate(template) for template in templates]


@router.get("/{template_id}", response_model=LogTemplateRead)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
) -> LogTemplateRead:
    """
    Get a single template by ID.
    
    Args:
        template_id: Template ID
        db: Database session
        
    Returns:
        LogTemplateRead: Template data
        
    Raises:
        HTTPException: If template not found
    """
    template = log_template_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return LogTemplateRead.model_validate(template)


@router.put("/{template_id}", response_model=LogTemplateRead)
def update_template(
    template_id: UUID,
    template_data: LogTemplateUpdate,
    db: Session = Depends(get_db)
) -> LogTemplateRead:
    """
    Update an existing template.
    
    Args:
        template_id: Template ID
        template_data: Template update data
        db: Database session
        
    Returns:
        LogTemplateRead: Updated template data
    """
    template = log_template_service.update_template(db, template_id, template_data)
    return LogTemplateRead.model_validate(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a template.
    
    Args:
        template_id: Template ID
        db: Database session
    """
    log_template_service.delete_template(db, template_id)


@router.post("/{template_id}/clone", response_model=LogTemplateRead, status_code=status.HTTP_201_CREATED)
def clone_template(
    template_id: UUID,
    db: Session = Depends(get_db)
) -> LogTemplateRead:
    """
    Clone an existing template.
    
    Args:
        template_id: Template ID to clone
        db: Database session
        
    Returns:
        LogTemplateRead: Cloned template data
    """
    cloned_template = log_template_service.clone_template(db, template_id)
    return LogTemplateRead.model_validate(cloned_template)