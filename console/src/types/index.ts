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






// API response types
export interface ApiError {
    detail: string;
}


