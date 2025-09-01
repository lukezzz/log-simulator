/**
 * TypeScript interfaces for Job and LogTemplate entities.
 * These interfaces match the Pydantic schemas from the backend API.
 */

// Enums as const objects
export const ProtocolEnum = {
    TCP: "TCP",
    UDP: "UDP",
} as const;

export type ProtocolEnum = typeof ProtocolEnum[keyof typeof ProtocolEnum];

export const JobStatusEnum = {
    IDLE: "IDLE",
    RUNNING: "RUNNING",
    STOPPED: "STOPPED",
    ERROR: "ERROR",
} as const;

export type JobStatusEnum = typeof JobStatusEnum[keyof typeof JobStatusEnum];

// Template placeholder formats
export const PlaceholderFormatEnum = {
    ECS: "ECS",
    LEGACY: "LEGACY",
    MIXED: "MIXED",
    STATIC: "STATIC",
} as const;

export type PlaceholderFormatEnum = typeof PlaceholderFormatEnum[keyof typeof PlaceholderFormatEnum];

// ECS Placeholder information
export interface ECSPlaceholderInfo {
    placeholder: string;
    description: string;
    example: string;
    category: string;
}

export interface PlaceholderAnalysis {
    ecsPlaceholders: number;
    legacyPlaceholders: number;
    hasECSFormat: boolean;
    hasLegacyFormat: boolean;
    format: PlaceholderFormatEnum;
}

// LogTemplate types
export interface LogTemplate {
    id: string;
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
    is_predefined: boolean;
    created_at: string;
    updated_at: string;
}

export interface LogTemplateCreate {
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
    is_predefined?: boolean;
}

export interface LogTemplateUpdate {
    name?: string;
    device_type?: string;
    content_format?: string;
    description?: string;
}

// Job types
export interface Job {
    id: string;
    template_id: string;
    protocol: ProtocolEnum;
    destination_host: string;
    destination_port: number;
    status: JobStatusEnum;
    start_time?: string;
    end_time?: string;
    send_count?: number;
    send_interval_ms?: number;
    created_at: string;
    updated_at: string;
}

export interface JobCreate {
    template_id: string;
    protocol: ProtocolEnum;
    destination_host: string;
    destination_port: number;
    start_time?: string;
    end_time?: string;
    send_count?: number;
    send_interval_ms?: number;
}

export interface JobUpdate {
    template_id?: string;
    protocol?: ProtocolEnum;
    destination_host?: string;
    destination_port?: number;
    status?: JobStatusEnum;
    start_time?: string;
    end_time?: string;
    send_count?: number;
    send_interval_ms?: number;
}

// API response types
export interface ApiError {
    detail: string;
}

// Form state types
export interface CreateJobFormData {
    template_id: string;
    protocol: ProtocolEnum;
    destination_host: string;
    destination_port: number;
    start_time?: string;
    end_time?: string;
    send_count?: number;
    send_interval_ms?: number;
}

// Form error types
export interface CreateJobFormErrors {
    template_id?: string;
    protocol?: string;
    destination_host?: string;
    destination_port?: string;
    start_time?: string;
    end_time?: string;
    send_count?: string;
    send_interval_ms?: string;
}

// Template form types
export interface TemplateFormData {
    name: string;
    device_type: string;
    content_format: string;
    description?: string;
}

export interface TemplateFormErrors {
    name?: string;
    device_type?: string;
    content_format?: string;
    description?: string;
}

// Log parsing types
export interface LogParseRequest {
    template_content_format: string;
    log_message: string;
}

export interface LogParseResponse {
    is_match: boolean;
    parsed_ecs?: Record<string, any>;
    error_message?: string;
}