"""
Database session management and dependency injection.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.settings import cfg


# Create database engine
engine = create_engine(
    cfg.APP_DB_URI,
    echo=cfg.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
