// Need to use the React-specific entry point to import createApi

import { baseApi } from "./base"

// Define a service using a base URL and expected endpoints
export const jobApi = baseApi.injectEndpoints({
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
    })
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useGetJobsQuery,
    useGetJobQuery,
    useCreateJobMutation,
    useUpdateJobMutation,
    useStartJobMutation,
    useStopJobMutation,
    useDeleteJobMutation,
} = jobApi