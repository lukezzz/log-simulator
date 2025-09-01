// Job types
interface Job {
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

interface JobCreate {
    template_id: string;
    protocol: ProtocolEnum;
    destination_host: string;
    destination_port: number;
    start_time?: string;
    end_time?: string;
    send_count?: number;
    send_interval_ms?: number;
}

interface JobUpdate {
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

// Form state types
interface CreateJobFormData {
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
interface CreateJobFormErrors {
    template_id?: string;
    protocol?: string;
    destination_host?: string;
    destination_port?: string;
    start_time?: string;
    end_time?: string;
    send_count?: string;
    send_interval_ms?: string;
}
