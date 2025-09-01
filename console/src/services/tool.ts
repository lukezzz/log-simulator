// Need to use the React-specific entry point to import createApi

import { baseApi } from "./base"

// Define a service using a base URL and expected endpoints
export const toolApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        parseLog: builder.mutation<LogParseResponse, LogParseRequest>({
            query: (requestData) => ({
                url: '/tools/parse-log',
                method: 'POST',
                body: requestData,
            }),
        }),

    })
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useParseLogMutation
} = toolApi