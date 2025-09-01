// Need to use the React-specific entry point to import createApi

import type { UserProps } from "@/types/user"
import { baseApi } from "./base"

// Define a service using a base URL and expected endpoints
export const authApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        getSelf: builder.query<CommonResponse<UserProps>, void>({
            query: () => {
                return {
                    url: '/api/v1/auth/self',
                    method: 'GET',
                }
            },
            providesTags: ["Auth"]
        }),
        login: builder.mutation({
            query: (data) => ({
                url: '/api/v1/auth/login',
                method: 'POST',
                body: data,
            }),
            // invalidatesTags: () => ["Auth"]
        }),
        logout: builder.mutation<unknown, void>({
            query: () => ({
                url: '/api/v1/auth/logout',
                method: 'POST',
            }),
        }),
        getSSOUrl: builder.mutation<CommonResponse<string>, { redirectUrl: string }>({
            query: ({ redirectUrl }) => '/api/v1/auth/saml_login?redirectUrl=' + redirectUrl,

        }),

    })
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const {
    useGetSelfQuery,
    useLoginMutation,
    useLogoutMutation,
    useGetSSOUrlMutation
} = authApi