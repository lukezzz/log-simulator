// LogTemplate types
interface LogTemplate {
    id: string;
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
    is_predefined: boolean;
    created_at: string;
    updated_at: string;
}

interface LogTemplateCreate {
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
    is_predefined?: boolean;
}

interface LogTemplateUpdate {
    name?: string;
    device_type?: string;
    content_format?: string;
    description?: string;
}


// Template form types
interface TemplateFormData {
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
}

interface TemplateFormErrors {
    name?: string;
    device_type?: string;
    content_format?: string;
    description?: string;
}
