// Need to use the React-specific entry point to import createApi

import { baseApi } from "./base"

// Define a service using a base URL and expected endpoints
export const templateApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
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
    })
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useGetTemplatesQuery,
    useGetTemplateQuery,
    useCreateTemplateMutation,
    useUpdateTemplateMutation,
    useDeleteTemplateMutation,
    useCloneTemplateMutation,
} = templateApi