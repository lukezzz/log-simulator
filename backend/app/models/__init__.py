"""
Import all models to ensure they are registered with SQLAlchemy.
"""
from .log_template import LogTemplate
from .job import Job
from .aaa import *

__all__ = ["LogTemplate", "Job"]