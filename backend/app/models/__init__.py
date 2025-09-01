"""
Import all models to ensure they are registered with SQLAlchemy.
"""
from .log_template import LogTemplate
from .job import Job

__all__ = ["LogTemplate", "Job"]