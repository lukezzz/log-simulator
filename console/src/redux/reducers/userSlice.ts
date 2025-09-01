import { createSlice, isAnyOf } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../../redux/store'
import type { UserState, UserProps } from '@/types/user';
import { authApi } from '@/services/auth';


const initialState: UserState = {
    data: undefined,
    isSessionTimeout: true,
    access_token: undefined,
    refresh_token: undefined,
    isAuthenticating: false,
};

export const userSlice = createSlice({
    name: 'user',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        userLogin: (state, action: PayloadAction<{
            access_token: string,
            refresh_token: string
        }>) => {
            state.isSessionTimeout = false;
            state.access_token = action.payload.access_token
            state.refresh_token = action.payload.refresh_token
            // wait getSelf result
            state.isAuthenticating = true
            return state
        },
        userLogout: () => initialState,
        setSessionTimeoutModal: (state, action: PayloadAction<boolean>) => {
            state.isSessionTimeout = action.payload
            return state
        },
        setUser: (state, action: PayloadAction<UserProps>) => {
            state.data = { ...action.payload }
        },
        setToken: (state, action: PayloadAction<{
            access_token: string,
            refresh_token: string
        }>) => {
            state.access_token = action.payload.access_token
            state.refresh_token = action.payload.refresh_token
            state.isAuthenticating = true
            state.isSessionTimeout = false
        },
        refreshToken: (state, action: PayloadAction<string>) => {
            state.access_token = action.payload
            state.isAuthenticating = false
            state.isSessionTimeout = false
        }
    },
    extraReducers: (builder) => {
        builder.addMatcher(
            isAnyOf(
                authApi.endpoints.getSelf.matchFulfilled,
            ),
            (state, { payload }) => {
                if (payload) {
                    state.data = payload.data
                    state.isAuthenticating = false
                    state.isSessionTimeout = false
                }
            }
        ).addMatcher(
            authApi.endpoints.logout.matchFulfilled || authApi.endpoints.logout.matchRejected,
            () => initialState
        ).addMatcher(
            authApi.endpoints.login.matchFulfilled,
            (state, { payload }) => {
                // state.access_token = payload.data.access_token
                // state.refresh_token = payload.data.refresh_token
                state.access_token = payload.access_token
                state.refresh_token = payload.refresh_token
                state.isAuthenticating = true  // wait getSelf result
                state.isSessionTimeout = false
            }
        )
    }
})

export const { userLogin, userLogout, setUser, setSessionTimeoutModal, setToken, refreshToken } = userSlice.actions


// Other code such as selectors can use the imported `RootState` type
export const selectUser = (state: RootState) => state.user

export default userSlice.reducer
