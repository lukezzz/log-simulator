
// Log parsing types
interface LogParseRequest {
    template_content_format: string;
    log_message: string;
}

interface LogParseResponse {
    is_match: boolean;
    parsed_ecs?: Record<string, any>;
    error_message?: string;
}