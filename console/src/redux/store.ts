import { configureStore } from '@reduxjs/toolkit'
import { rootReducer } from "./reducers";
import {
    persistStore,
    persistReducer,
    createMigrate,
    FLUSH,
    REHYDRATE,
    PAUSE,
    PERSIST,
    PURGE,
    REGISTER,
} from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { setupListeners } from '@reduxjs/toolkit/query'
import { migrations } from './migrations'
import { baseApi } from '@/services/base';


const persistConfig = {
    key: 'root',
    storage,
    version: 0.01,
    blacklist: ['baseApi'],
    migrate: createMigrate(migrations, { debug: true })
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

// const middlewareHandler = (getDefaultMiddleware: any) => {
//     const middlewareList = [
//         ...getDefaultMiddleware({
//             serializableCheck: {
//                 ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
//             },
//             // serializableCheck: false
//         }),
//         baseApi.middleware,
//     ];
//     if (import.meta.env.MODE === 'development') {
//         // middlewareList.push(logger);
//     }
//     return middlewareList;
// }


export const store = configureStore({
    reducer: persistedReducer,
    devTools: import.meta.env.MODE !== 'production',
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
        }).concat(baseApi.middleware),
})



export const persistor = persistStore(store)

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch

// optional, but required for refetchOnFocus/refetchOnReconnect behaviors
// see `setupListeners` docs - takes an optional callback as the 2nd arg for customization
setupListeners(store.dispatch)


