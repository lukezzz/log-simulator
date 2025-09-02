"""
Database initialization with default data.
"""
import argparse
import os
import sys
import uuid
import yaml
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the parent directory to sys.path to import from app modules
sys.path.append(str(Path(__file__).parent.parent))

from models.base import BaseModel
from models.log_template import LogTemplate
from models.aaa import Role, Permission, Account
from schemas.account import RoleNames, Permissions, PermissionRules
from core.security import get_password_hash
from core.db.session import engine, SessionLocal


def create_database_tables() -> None:
    """
    Create all database tables.
    """
    print("Creating database tables...")
    try:
        BaseModel.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)


def drop_database_tables() -> None:
    """
    Drop all database tables.
    """
    print("Dropping database tables...")
    try:
        BaseModel.metadata.drop_all(bind=engine)
        print("Database tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping database tables: {e}")
        sys.exit(1)


def create_default_log_templates(db: Session) -> None:
    """
    Create default log templates if they don't exist by loading them from YAML files.
    
    Args:
        db: Database session
    """

    
    # Load templates from YAML files
    templates_dir = Path(__file__).parent.parent.parent / "predefined_templates"
    
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


def create_default_admin_user(db: Session, password: str = "secret") -> None:
    """
    Create default admin user if it doesn't exist.
    
    Args:
        db: Database session
        password: Password for the admin user
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
                password_hashed=get_password_hash(password),
                desc="Default system administrator",
                is_blocked=False,
                role_id=admin_role.id,
                user_type="local",
                id=str(uuid.uuid4())
            )
            
            db.add(admin_user)
            db.commit()
            print(f"Created default admin user with password '{password}'")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()


def initialize_aaa_data(db: Session, admin_password: str = "secret") -> None:
    """
    Initialize all AAA (Authentication, Authorization, Accounting) data.
    
    Args:
        db: Database session
        admin_password: Password for the admin user
    """
    print("Initializing AAA data...")
    create_default_permissions(db)
    create_default_roles(db)
    create_default_admin_user(db, admin_password)
    print("AAA data initialization completed.")


def init_db_data(db: Session, admin_password: str = "secret") -> None:
    """
    Initialize all database data.
    
    Args:
        db: Database session
        admin_password: Password for the admin user
    """
    print("Starting database initialization...")
    create_default_log_templates(db)
    initialize_aaa_data(db, admin_password)
    print("Database initialization completed.")


def main():
    """
    Main function with command line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="Database initialization script for Log Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --create-tables --init-data    # Create tables and initialize data
  %(prog)s --drop-tables                  # Drop all tables
  %(prog)s --init-data                    # Initialize data only
  %(prog)s --create-admin                 # Create admin user only
  %(prog)s --reset                        # Drop and recreate everything
        """
    )
    
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create database tables"
    )
    
    parser.add_argument(
        "--drop-tables",
        action="store_true",
        help="Drop database tables"
    )
    
    parser.add_argument(
        "--init-data",
        action="store_true",
        help="Initialize database with default data"
    )
    
    parser.add_argument(
        "--init-templates",
        action="store_true",
        help="Initialize log templates only"
    )
    
    parser.add_argument(
        "--init-aaa",
        action="store_true",
        help="Initialize AAA (authentication, authorization, accounting) data only"
    )
    
    parser.add_argument(
        "--create-admin",
        action="store_true",
        help="Create default admin user only"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (drop tables, create tables, and initialize data)"
    )
    
    parser.add_argument(
        "--admin-password",
        type=str,
        default="secret",
        help="Password for the default admin user (default: secret)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operations without confirmation prompts"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any([
        args.create_tables, args.drop_tables, args.init_data,
        args.init_templates, args.init_aaa, args.create_admin, args.reset
    ]):
        parser.print_help()
        return
    
    # Confirmation for destructive operations
    if args.drop_tables or args.reset:
        if not args.force:
            confirm = input("This will drop existing database tables. Are you sure? (y/N): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return
    
    try:
        # Handle reset operation
        if args.reset:
            drop_database_tables()
            create_database_tables()
            with SessionLocal() as db:
                init_db_data(db, args.admin_password)
            return
        
        # Handle table operations
        if args.drop_tables:
            drop_database_tables()
        
        if args.create_tables:
            create_database_tables()
        
        # Handle data initialization operations
        with SessionLocal() as db:
            if args.init_data:
                init_db_data(db, args.admin_password)
            elif args.init_templates:
                create_default_log_templates(db)
            elif args.init_aaa:
                initialize_aaa_data(db, args.admin_password)
            elif args.create_admin:
                create_default_admin_user(db, args.admin_password)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()