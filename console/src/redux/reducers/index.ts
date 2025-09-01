import { combineReducers } from "redux";
import configReducer from "./configSlice";
// import dagReducer from './dagReducer'
import userReducer from "./userSlice";
import { baseApi } from "@/services/base";

export const rootReducer = combineReducers({
    config: configReducer,
    user: userReducer,
    [baseApi.reducerPath]: baseApi.reducer,
});
