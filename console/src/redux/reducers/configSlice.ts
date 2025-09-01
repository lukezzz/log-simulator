import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '../store'


const initialState: ConfigState = {
    remember: true,
    theme: "light",
    menuCollapsed: false,
    pageSize: 10,
    dashboardTheme: "light",
    locale: "en",
};

export const configSlice = createSlice({
    name: 'config',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        setConfig: (state, action: PayloadAction<ConfigState>) => {
            state = { ...state, ...action.payload }
            return state
        }
    },
})

export const { setConfig } = configSlice.actions


// Other code such as selectors can use the imported `RootState` type
export const selectConfig = (state: RootState) => state.config

export default configSlice.reducer
