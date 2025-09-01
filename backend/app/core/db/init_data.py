"""
Database initialization with default data.
"""
import os
import uuid
import yaml
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.log_template import LogTemplate
from models.aaa import Role, Permission, Account
from schemas.account import RoleNames, Permissions, PermissionRules
from core.security import get_password_hash


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


def create_default_permissions(db: Session) -> None:
    """
    Create default permissions if they don't exist.
    
    Args:
        db: Database session
    """
    try:
        for permission in Permissions:
            existing_permission = db.query(Permission).filter(
                Permission.name == permission.value
            ).first()
            
            if not existing_permission:
                new_permission = Permission(name=permission.value)
                db.add(new_permission)
                print(f"Created permission: {permission.value}")
            else:
                print(f"Permission already exists: {permission.value}")
        
        db.commit()
        
    except Exception as e:
        print(f"Error creating permissions: {e}")
        db.rollback()


def create_default_roles(db: Session) -> None:
    """
    Create default roles with their associated permissions if they don't exist.
    
    Args:
        db: Database session
    """
    try:
        # First ensure all permissions exist
        create_default_permissions(db)
        
        for role_name in RoleNames:
            existing_role = db.query(Role).filter(
                Role.name == role_name.value
            ).first()
            
            if not existing_role:
                # Create new role
                new_role = Role(name=role_name.value)
                db.add(new_role)
                db.flush()  # Flush to get the ID
                
                # Get permissions for this role from PermissionRules
                if hasattr(PermissionRules, role_name.value):
                    role_permissions = getattr(PermissionRules, role_name.value).value
                    
                    # Add permissions to role using direct database queries to avoid UUID issues
                    for perm_name in role_permissions:
                        permission = db.query(Permission).filter(
                            Permission.name == perm_name
                        ).first()
                        if permission:
                            # Use direct SQL to insert into association table to handle UUID properly
                            db.execute(
                                text(
                                    "INSERT INTO aaa_role_permission (role_id, permission_id) VALUES (:role_id, :permission_id)"
                                ),
                                {
                                    "role_id": str(new_role.id), 
                                    "permission_id": str(permission.id)
                                }
                            )
                
                print(f"Created role: {role_name.value}")
            else:
                print(f"Role already exists: {role_name.value}")
        
        db.commit()
        
    except Exception as e:
        print(f"Error creating roles: {e}")
        db.rollback()


def create_default_admin_user(db: Session) -> None:
    """
    Create default admin user if it doesn't exist.
    
    Args:
        db: Database session
    """
    try:
        # Check if admin user already exists
        existing_admin = db.query(Account).filter(
            Account.username == "admin"
        ).first()
        
        if not existing_admin:
            # Get admin role
            admin_role = db.query(Role).filter(
                Role.name == RoleNames.admin.value
            ).first()
            
            if not admin_role:
                print("Error: Admin role not found. Please ensure roles are created first.")
                return
            
            # Create admin user
            admin_user = Account(
                username="admin",
                display_name="Administrator",
                email="admin@logsimulator.local",
                first_name="System",
                last_name="Administrator",
                password_hashed=get_password_hash("secret"),
                desc="Default system administrator",
                is_blocked=False,
                role_id=admin_role.id,
                user_type="local",
                id=str(uuid.uuid4())
            )
            
            db.add(admin_user)
            db.commit()
            print("Created default admin user with password 'secret'")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()


def initialize_aaa_data(db: Session) -> None:
    """
    Initialize all AAA (Authentication, Authorization, Accounting) data.
    
    Args:
        db: Database session
    """
    print("Initializing AAA data...")
    create_default_permissions(db)
    create_default_roles(db)
    create_default_admin_user(db)
    print("AAA data initialization completed.")


def init_db_data(db: Session) -> None:
    """
    Initialize all database data.
    
    Args:
        db: Database session
    """
    print("Starting database initialization...")
    create_default_log_templates(db)
    initialize_aaa_data(db)
    print("Database initialization completed.")