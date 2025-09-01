/**
 * RTK Query API service for the Log Simulator backend.
 */
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type {
    Job,
    JobCreate,
    JobUpdate,
    LogTemplate,
    LogTemplateCreate,
    LogTemplateUpdate,
    LogParseRequest,
    LogParseResponse,
} from '../types';

// Base API configuration
export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: 'http://localhost:8000/api/v1',
        prepareHeaders: (headers) => {
            headers.set('Content-Type', 'application/json');
            return headers;
        },
    }),
    tagTypes: ['Job', 'Template'],
    endpoints: (builder) => ({
        // Job endpoints
        getJobs: builder.query<Job[], { skip?: number; limit?: number }>({
            query: ({ skip = 0, limit = 100 } = {}) => ({
                url: '/jobs/',
                params: { skip, limit },
            }),
            providesTags: ['Job'],
        }),

        getJob: builder.query<Job, string>({
            query: (jobId) => `/jobs/${jobId}`,
            providesTags: (_result, _error, jobId) => [{ type: 'Job', id: jobId }],
        }),

        createJob: builder.mutation<Job, JobCreate>({
            query: (jobData) => ({
                url: '/jobs',
                method: 'POST',
                body: jobData,
            }),
            invalidatesTags: ['Job'],
        }),

        updateJob: builder.mutation<Job, { jobId: string; jobData: JobUpdate }>({
            query: ({ jobId, jobData }) => ({
                url: `/jobs/${jobId}`,
                method: 'PUT',
                body: jobData,
            }),
            invalidatesTags: (_result, _error, { jobId }) => [
                { type: 'Job', id: jobId },
                'Job',
            ],
        }),

        startJob: builder.mutation<Job, string>({
            query: (jobId) => ({
                url: `/jobs/${jobId}/start`,
                method: 'POST',
            }),
            invalidatesTags: (_result, _error, jobId) => [
                { type: 'Job', id: jobId },
                'Job',
            ],
        }),

        stopJob: builder.mutation<Job, string>({
            query: (jobId) => ({
                url: `/jobs/${jobId}/stop`,
                method: 'POST',
            }),
            invalidatesTags: (_result, _error, jobId) => [
                { type: 'Job', id: jobId },
                'Job',
            ],
        }),

        deleteJob: builder.mutation<void, string>({
            query: (jobId) => ({
                url: `/jobs/${jobId}`,
                method: 'DELETE',
            }),
            invalidatesTags: (_result, _error, jobId) => [
                { type: 'Job', id: jobId },
                'Job',
            ],
        }),

        // Template endpoints
        getTemplates: builder.query<LogTemplate[], { skip?: number; limit?: number }>({
            query: ({ skip = 0, limit = 100 } = {}) => ({
                url: '/templates/',
                params: { skip, limit },
            }),
            providesTags: ['Template'],
        }),

        getTemplate: builder.query<LogTemplate, string>({
            query: (templateId) => `/templates/${templateId}`,
            providesTags: (_result, _error, templateId) => [{ type: 'Template', id: templateId }],
        }),

        createTemplate: builder.mutation<LogTemplate, LogTemplateCreate>({
            query: (templateData) => ({
                url: '/templates',
                method: 'POST',
                body: templateData,
            }),
            invalidatesTags: ['Template'],
        }),

        updateTemplate: builder.mutation<LogTemplate, { templateId: string; templateData: LogTemplateUpdate }>({
            query: ({ templateId, templateData }) => ({
                url: `/templates/${templateId}`,
                method: 'PUT',
                body: templateData,
            }),
            invalidatesTags: (_result, _error, { templateId }) => [
                { type: 'Template', id: templateId },
                'Template',
            ],
        }),

        deleteTemplate: builder.mutation<void, string>({
            query: (templateId) => ({
                url: `/templates/${templateId}`,
                method: 'DELETE',
            }),
            invalidatesTags: (_result, _error, templateId) => [
                { type: 'Template', id: templateId },
                'Template',
            ],
        }),

        cloneTemplate: builder.mutation<LogTemplate, string>({
            query: (templateId) => ({
                url: `/templates/${templateId}/clone`,
                method: 'POST',
            }),
            invalidatesTags: ['Template'],
        }),

        // Tools endpoints
        parseLog: builder.mutation<LogParseResponse, LogParseRequest>({
            query: (requestData) => ({
                url: '/tools/parse-log',
                method: 'POST',
                body: requestData,
            }),
        }),
    }),
});

// Export hooks for usage in functional components
export const {
    useGetJobsQuery,
    useGetJobQuery,
    useCreateJobMutation,
    useUpdateJobMutation,
    useStartJobMutation,
    useStopJobMutation,
    useDeleteJobMutation,
    useGetTemplatesQuery,
    useGetTemplateQuery,
    useCreateTemplateMutation,
    useUpdateTemplateMutation,
    useDeleteTemplateMutation,
    useCloneTemplateMutation,
    useParseLogMutation,
} = api;