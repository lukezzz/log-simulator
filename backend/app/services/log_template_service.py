"""
Service layer for template management business logic.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from models.log_template import LogTemplate
from schemas.log_template import LogTemplateCreate, LogTemplateUpdate


def create_template(db: Session, template_data: LogTemplateCreate) -> LogTemplate:
    """
    Create a new log template.
    
    Args:
        db: Database session
        template_data: Template creation data
        
    Returns:
        LogTemplate: Created template instance
    """
    db_template = LogTemplate(
        name=template_data.name,
        device_type=template_data.device_type,
        content_format=template_data.content_format,
        description=template_data.description,
        is_predefined=template_data.is_predefined
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


def get_templates(db: Session, skip: int = 0, limit: int = 100) -> List[LogTemplate]:
    """
    Get all templates with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[LogTemplate]: List of templates
    """
    statement = select(LogTemplate).offset(skip).limit(limit)
    result = db.execute(statement)
    return result.scalars().all()


def get_template_by_id(db: Session, template_id: UUID) -> Optional[LogTemplate]:
    """
    Get a template by its ID.
    
    Args:
        db: Database session
        template_id: Template ID
        
    Returns:
        LogTemplate: Template instance or None if not found
    """
    statement = select(LogTemplate).where(LogTemplate.id == template_id)
    result = db.execute(statement)
    return result.scalar_one_or_none()


def update_template(db: Session, template_id: UUID, template_data: LogTemplateUpdate) -> LogTemplate:
    """
    Update an existing log template.
    
    Args:
        db: Database session
        template_id: Template ID
        template_data: Template update data
        
    Returns:
        LogTemplate: Updated template instance
        
    Raises:
        HTTPException: If template not found or is predefined
    """
    db_template = get_template_by_id(db, template_id)
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    if db_template.is_predefined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify predefined templates"
        )
    
    # Update only provided fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template


def delete_template(db: Session, template_id: UUID) -> bool:
    """
    Delete a log template.
    
    Args:
        db: Database session
        template_id: Template ID
        
    Returns:
        bool: True if deleted successfully
        
    Raises:
        HTTPException: If template not found or is predefined
    """
    db_template = get_template_by_id(db, template_id)
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    if db_template.is_predefined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete predefined templates"
        )
    
    db.delete(db_template)
    db.commit()
    
    return True


def clone_template(db: Session, template_id: UUID) -> LogTemplate:
    """
    Clone an existing log template.
    
    Args:
        db: Database session
        template_id: Template ID to clone
        
    Returns:
        LogTemplate: Cloned template instance
        
    Raises:
        HTTPException: If template not found
    """
    source_template = get_template_by_id(db, template_id)
    
    if not source_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Create a new template with copied data
    cloned_template = LogTemplate(
        name=f"{source_template.name} (copy)",
        device_type=source_template.device_type,
        content_format=source_template.content_format,
        description=f"Cloned from: {source_template.name}",
        is_predefined=False  # Cloned templates are never predefined
    )
    
    db.add(cloned_template)
    db.commit()
    db.refresh(cloned_template)
    
    return cloned_template