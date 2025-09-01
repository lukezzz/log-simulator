import re
from typing import Dict, Any, Optional
from schemas.tools import LogParseResponse


def convert_template_to_regex(template: str) -> str:
    """
    Convert a template string with {place.holder} syntax to a regex pattern.
    
    Args:
        template: Template string like "srcip={source.ip} dstip={dest.ip}"
        
    Returns:
        Regex pattern with named capture groups
    """
    # First, extract placeholders before escaping
    placeholder_pattern = r'\{([^}]+)\}'
    placeholders = []
    
    def extract_placeholder(match):
        placeholder = match.group(1)
        placeholders.append(placeholder)
        # Return a temporary marker that we'll replace later
        return f"__PLACEHOLDER_{len(placeholders)-1}__"
    
    # Replace placeholders with temporary markers
    temp_template = re.sub(placeholder_pattern, extract_placeholder, template)
    
    # Now escape the template (which no longer contains placeholders)
    escaped_template = re.escape(temp_template)
    
    # Replace the temporary markers with regex groups
    for i, placeholder in enumerate(placeholders):
        # Create valid regex group name by replacing dots and other invalid chars
        group_name = re.sub(r'[^a-zA-Z0-9_]', '_', placeholder)
        marker = re.escape(f"__PLACEHOLDER_{i}__")
        # Use non-greedy matching that stops at whitespace or end of string
        escaped_template = escaped_template.replace(marker, f'(?P<{group_name}>[^\\s]+)')
    
    return escaped_template


def unflatten_dict(flat_dict: Dict[str, str], original_placeholders: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert a flat dictionary with sanitized group names back to nested dictionary.
    
    Args:
        flat_dict: Flat dict like {'source_ip': '1.2.3.4', 'dest_port': '80'}
        original_placeholders: Mapping from sanitized names to original placeholder names
        
    Returns:
        Nested dict like {'source': {'ip': '1.2.3.4'}, 'dest': {'port': '80'}}
    """
    result = {}
    
    for sanitized_key, value in flat_dict.items():
        # Get the original placeholder name
        original_key = original_placeholders.get(sanitized_key, sanitized_key)
        keys = original_key.split('.')
        
        # Navigate/create the nested structure
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    return result


def parse_log_with_template(template_content_format: str, log_message: str) -> LogParseResponse:
    """
    Parse a log message using a template to extract structured ECS data.
    
    Args:
        template_content_format: Template string with placeholders like "srcip={source.ip}"
        log_message: Raw log message to parse like "srcip=1.2.3.4"
        
    Returns:
        LogParseResponse with parsing results
    """
    try:
        # Extract placeholders for mapping back later
        placeholder_pattern = r'\{([^}]+)\}'
        placeholders = re.findall(placeholder_pattern, template_content_format)
        
        # Create mapping from sanitized names back to original placeholders
        original_placeholders = {}
        for placeholder in placeholders:
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', placeholder)
            original_placeholders[sanitized] = placeholder
        
        # Convert template to regex pattern
        regex_pattern = convert_template_to_regex(template_content_format)
        
        # Try to match the log message against the pattern
        match = re.match(regex_pattern, log_message)
        
        if not match:
            return LogParseResponse(
                is_match=False,
                error_message="Log message does not match the template pattern"
            )
        
        # Extract the matched groups
        flat_data = match.groupdict()
        
        # Convert to nested ECS format
        structured_data = unflatten_dict(flat_data, original_placeholders)
        
        return LogParseResponse(
            is_match=True,
            parsed_ecs=structured_data
        )
        
    except Exception as e:
        return LogParseResponse(
            is_match=False,
            error_message=f"Error parsing log: {str(e)}"
        )