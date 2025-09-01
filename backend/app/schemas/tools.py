from typing import Optional, Dict, Any
from pydantic import BaseModel


class LogParseRequest(BaseModel):
    """Request schema for parsing a log message with a template."""
    
    template_content_format: str
    log_message: str


class LogParseResponse(BaseModel):
    """Response schema for log parsing result."""
    
    is_match: bool
    parsed_ecs: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None