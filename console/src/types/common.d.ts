type PaginationType = {
    current?: number;
    pageSize?: number;
};


type SearchStringType = {
    query?: QueryType;
};


type TableListResponse<T> = PaginationType & {
    total: number
    items: T[]
}

type CommonListResponse<T> = {
    data: T[]
    success: boolean
}

type CommonResponse<T> = {
    data: T
    success: boolean
}

type CommonSelectProps = {
    id: string;
    name: string;
};


interface UploadOptions {
    onProgress?: (event: UploadProgressEvent) => void;
    onError?: (event: UploadRequestError | ProgressEvent, body?: T) => void;
    onSuccess?: (body: T, xhr?: XMLHttpRequest) => void;
    data?: Record<string, unknown>;
    filename?: string;
    file: Exclude<BeforeUploadFileType, File | boolean> | RcFile;
    withCredentials?: boolean;
    action: string;
    headers?: UploadRequestHeader;
    method: UploadRequestMethod;
}


type DateRangeQueryType = {
    start_time: string;
    end_time: string;
};

interface ConfigState {
    remember?: boolean;
    theme?: ThemeName
    menuCollapsed?: boolean;
    pageSize?: number;
    dashboardTheme?: DashboardThemeName;
    locale?: string;
}