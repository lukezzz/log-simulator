"""
Database initialization with default data.
"""
import argparse
import logging
import os
import sys
import uuid
import yaml
from pathlib import Path
from sqlalchemy import text
import asyncio

# Add the parent directory to sys.path to import from app modules
sys.path.append(str(Path(__file__).parent.parent))

from core.fastapi_logger import fastapi_logger as logger
from models.base import BaseModel
from models.log_template import LogTemplate
from models.aaa import Role, Permission, Account
from schemas.account import RoleNames, Permissions, PermissionRules
from core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from core.postgres_engine import Base
from sqlalchemy import select
from core.settings import cfg


async def create_database_tables(engine: AsyncEngine):
    async with engine.begin() as db:
        # enable the extension
        logger.info("start init db")

        logger.warning("Creating tables and indexes")
        await db.run_sync(Base.metadata.create_all)

        logger.info("end init vector")

    await db.close()


async def drop_database_tables() -> None:
    """
    Drop all database tables.
    """
    print("Dropping database tables...")
    try:
        engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("Database tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping database tables: {e}")
        sys.exit(1)


async def create_default_log_templates(engine: AsyncEngine) -> None:
    """
    Create default log templates if they don't exist by loading them from YAML files.
    
    Args:
        engine: AsyncEngine
    """

    async with AsyncSession(engine) as session:
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
                result = await session.execute(select(LogTemplate).where(LogTemplate.name == template_data['name']))
                existing_template = result.scalars().first()
                print(f"debug==== Type: {type(existing_template)}, Value: {existing_template}")
                if existing_template:
                    print(f"Template details - ID: {existing_template.id}, Name: {existing_template.name}, Device: {existing_template.device_type}")

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
                    session.add(new_template)
                    print(f"Created new template: {template_data['name']}")
                
                await session.commit()
                
            except Exception as e:
                print(f"Error processing template file {yaml_file}: {e}")
                await session.rollback()


async def create_default_permissions(engine: AsyncEngine) -> None:
    """
    Create default permissions if they don't exist.
    
    Args:
    engine: AsyncEngine
    """
    async with AsyncSession(engine) as conn:
        try:
            for permission in Permissions:
                res = await conn.execute(select(Permission).where(
                    Permission.name == permission.value
                ))
                existing_permission = await res.scalars().first()

                if not existing_permission:
                    new_permission = Permission(name=permission.value)
                    conn.add(new_permission)
                    print(f"Created permission: {permission.value}")
                else:
                    print(f"Permission already exists: {permission.value}")

            await conn.commit()
            
        except Exception as e:
            print(f"Error creating permissions: {e}")
            await conn.rollback()


async def create_default_roles(engine: AsyncEngine) -> None:
    """
    Create default roles with their associated permissions if they don't exist.
    
    Args:
        db: Database session
    """
    async with AsyncSession(engine) as conn:
        try:
            # First ensure all permissions exist
            await create_default_permissions(conn)

            for role_name in RoleNames:
                res = await conn.execute(select(Role).where(
                    Role.name == role_name.value
                ))
                existing_role = await res.scalars().first()

                if not existing_role:
                    # Create new role
                    new_role = Role(name=role_name.value)
                    conn.add(new_role)
                    await conn.flush()  # Flush to get the ID

                # Get permissions for this role from PermissionRules
                if hasattr(PermissionRules, role_name.value):
                    role_permissions = getattr(PermissionRules, role_name.value).value
                    
                    # Add permissions to role using direct database queries to avoid UUID issues
                    for perm_name in role_permissions:
                        permission_res = await conn.execute(select(Permission).where(
                            Permission.name == perm_name
                        ))
                        permission = await permission_res.scalars().first()
                        if permission:
                            # Use direct SQL to insert into association table to handle UUID properly
                            await conn.execute(
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
            
            await conn.commit()
            
        except Exception as e:
            print(f"Error creating roles: {e}")
            await conn.rollback()


async def create_default_admin_user(engine: AsyncEngine, password: str = "secret") -> None:
    """
    Create default admin user if it doesn't exist.
    
    Args:
        engine: AsyncEngine
        password: Password for the admin user
    """
    async with AsyncSession(engine) as conn:
        try:
            # Check if admin user already exists
            res = await conn.execute(select(Account).where(
                Account.username == "admin"
            ))
            existing_admin = await res.scalars().first()

            if not existing_admin:
                # Get admin role
                admin_role_res = await conn.execute(select(Role).where(
                    Role.name == RoleNames.admin.value
                ))
                admin_role = await admin_role_res.scalars().first()

                if not admin_role:
                    print("Error: Admin role not found. Please ensure roles are created first.")
                    return

                # Create admin user
                admin_user = Account(
                    username="admin",
                    role_id=admin_role.id
                )

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
                
                conn.add(admin_user)
                await conn.commit()
                print(f"Created default admin user with password '{password}'")
            else:
                print("Admin user already exists")
                
        except Exception as e:
            print(f"Error creating admin user: {e}")
            await conn.rollback()


async def initialize_aaa_data(engine: AsyncEngine, admin_password: str = "secret") -> None:
    """
    Initialize all AAA (Authentication, Authorization, Accounting) data.
    
    Args:
        db: Database session
        admin_password: Password for the admin user
    """
    print("Initializing AAA data...")
    await create_default_permissions(engine)
    await create_default_roles(engine)
    await create_default_admin_user(engine, admin_password)
    print("AAA data initialization completed.")


async def init_db_data(engine: AsyncEngine, admin_password: str = "secret") -> None:
    """
    Initialize all database data.
    
    Args:
        db: Database session
        admin_password: Password for the admin user
    """
    print("Starting database initialization...")
    await create_default_log_templates(engine)
    await initialize_aaa_data(engine, admin_password)
    print("Database initialization completed.")


async def main():
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
            await drop_database_tables()
            await create_database_tables()
            await init_db_data(args.admin_password)
            return
        
        # Handle table operations
        if args.drop_tables:
            await drop_database_tables()
        
        if args.create_tables:
            await create_database_tables()

        # Handle data initialization operations
        engine = create_async_engine(cfg.APP_DB_URI, echo=True)
        if args.init_data:
            await init_db_data(engine, args.admin_password)
        elif args.init_templates:
            await create_default_log_templates(engine)
        elif args.init_aaa:
            await initialize_aaa_data(engine, args.admin_password)
        elif args.create_admin:
            await create_default_admin_user(engine, args.admin_password)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)
    asyncio.run(main())