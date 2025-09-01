"""
API router for tools and utilities endpoints.
"""
from fastapi import APIRouter, status
from schemas.tools import LogParseRequest, LogParseResponse
from services.parsing_service import parse_log_with_template


router = APIRouter(
    prefix="/api/v1/tools",
    tags=["tools"]
)


@router.post("/parse-log", response_model=LogParseResponse, status_code=status.HTTP_200_OK)
def parse_log(
    request: LogParseRequest
) -> LogParseResponse:
    """
    Parse a log message using a template to extract structured ECS data.
    
    Args:
        request: Log parsing request containing template and log message
        
    Returns:
        LogParseResponse: Parsing result with structured data or error message
    """
    return parse_log_with_template(
        template_content_format=request.template_content_format,
        log_message=request.log_message
    )