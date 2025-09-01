"""
Database initialization with default data.
"""
import os
import yaml
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.log_template import LogTemplate


def create_default_log_templates(db: Session) -> None:
    """
    Create default log templates if they don't exist by loading them from YAML files.
    
    Args:
        db: Database session
    """
    # Handle schema migration for existing databases
    try:
        # Try to add new columns if they don't exist
        db.execute(text("ALTER TABLE log_templates ADD COLUMN IF NOT EXISTS description TEXT"))
        db.execute(text("ALTER TABLE log_templates ADD COLUMN IF NOT EXISTS is_predefined BOOLEAN DEFAULT FALSE"))
        
        # Add new job columns if they don't exist
        db.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS start_time TIMESTAMPTZ"))
        db.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS end_time TIMESTAMPTZ"))
        db.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS send_count INTEGER"))
        db.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS send_interval_ms INTEGER DEFAULT 1000"))
        
        db.commit()
    except Exception as e:
        print(f"Schema migration note: {e}")
        db.rollback()
    
    # Load templates from YAML files
    templates_dir = Path(__file__).parent.parent.parent.parent / "predefined_templates"
    
    if not templates_dir.exists():
        print(f"Predefined templates directory not found: {templates_dir}")
        return
    
    # Process all .yml files in the templates directory
    for yaml_file in templates_dir.glob("*.yml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            # Check if template with this name already exists
            existing_template = db.query(LogTemplate).filter(
                LogTemplate.name == template_data['name']
            ).first()
            
            if existing_template:
                # Update existing template
                existing_template.device_type = template_data['device_type']
                existing_template.content_format = template_data['content_format']
                existing_template.description = template_data['description']
                existing_template.is_predefined = True
                print(f"Updated existing template: {template_data['name']}")
            else:
                # Create new template
                new_template = LogTemplate(
                    name=template_data['name'],
                    device_type=template_data['device_type'],
                    content_format=template_data['content_format'],
                    description=template_data['description'],
                    is_predefined=True
                )
                db.add(new_template)
                print(f"Created new template: {template_data['name']}")
            
            db.commit()
            
        except Exception as e:
            print(f"Error processing template file {yaml_file}: {e}")
            db.rollback()