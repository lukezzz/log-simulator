"""
API router for template management endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from schemas.log_template import LogTemplateCreate, LogTemplateRead, LogTemplateUpdate
from services import log_template_service
from core.custom_api_route import HandleResponseRoute
from schemas.account import Permissions
from core.dependencies.db import DBSession
from core.dependencies.aaa import require_permissions
from core.custom_page import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from models.log_template import LogTemplate

router = APIRouter(
    route_class=HandleResponseRoute,
    tags=["templates"]
)


@router.post("/", response_model=LogTemplateRead, status_code=status.HTTP_201_CREATED)
@require_permissions(Permissions.admin)
async def create_template(
    template_data: LogTemplateCreate,
    db: DBSession
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


@router.get("/list", response_model=Page[LogTemplateRead])
async def get_templates(
    db: DBSession,
    name: Optional[str] = None,
    device_type: Optional[str] = None,
    content_format: Optional[str] = None,
) -> Page[LogTemplateRead]:
    """
    Get a list of all templates with pagination and optional filters.
    
    Args:
        db: Database session
        name: Optional filter by template name
        device_type: Optional filter by device type
        content_format: Optional filter by content format
        
    Returns:
        Page[LogTemplateRead]: Paginated list of templates
    """
    query = select(LogTemplate)
    
    if name and name != "undefined":
        query = query.filter(LogTemplate.name.ilike(f"%{name}%"))
    if device_type:
        query = query.filter(LogTemplate.device_type == device_type)
    if content_format:
        query = query.filter(LogTemplate.content_format == content_format)
    
    return await paginate(db, query)


@router.get("/{template_id}", response_model=LogTemplateRead)
async def get_template(
    template_id: UUID,
    db: DBSession
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
async def update_template(
    template_id: UUID,
    template_data: LogTemplateUpdate,
    db: DBSession
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
async def delete_template(
    template_id: UUID,
    db: DBSession
) -> None:
    """
    Delete a template.
    
    Args:
        template_id: Template ID
        db: Database session
    """
    log_template_service.delete_template(db, template_id)


@router.post("/{template_id}/clone", response_model=LogTemplateRead, status_code=status.HTTP_201_CREATED)
async def clone_template(
    template_id: UUID,
    db: DBSession
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