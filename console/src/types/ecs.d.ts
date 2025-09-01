// Template placeholder formats
const PlaceholderFormatEnum = {
    ECS: "ECS",
    LEGACY: "LEGACY",
    MIXED: "MIXED",
    STATIC: "STATIC",
} as const;

type PlaceholderFormatEnum = typeof PlaceholderFormatEnum[keyof typeof PlaceholderFormatEnum];

// ECS Placeholder information
interface ECSPlaceholderInfo {
    placeholder: string;
    description: string;
    example: string;
    category: string;
}

interface PlaceholderAnalysis {
    ecsPlaceholders: number;
    legacyPlaceholders: number;
    hasECSFormat: boolean;
    hasLegacyFormat: boolean;
    format: PlaceholderFormatEnum;
}
