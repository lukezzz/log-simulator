import {
  createApi,
  fetchBaseQuery
} from '@reduxjs/toolkit/query/react';
import type {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
  FetchBaseQueryMeta,
  QueryReturnValue,
} from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/redux/store';
import { refreshToken, userLogout } from '@/redux/reducers/userSlice';
import { message } from 'antd';

const baseUrl: string = import.meta.env.VITE_API_URL as string;

export interface IResponseSuccess {
  success: boolean;
  errorMessage?: string;
  data?: Record<string, unknown> | number | string;
}

export interface IResponseError422 {
  loc: string[];
  msg: string;
  type: string;
}

export interface IResponseError {
  success: boolean;
  data?: string;
  errorMessage?: string | IResponseError422[];
  traceId?: string;
  app?: string;
}

// export const getCookie = (cookieName: string): string | undefined => {
//   const cookieArray = document.cookie.split(';');

//   for (const cookie of cookieArray) {
//     let cookieString = cookie;

//     while (cookieString.charAt(0) == ' ') {
//       cookieString = cookieString.substring(1, cookieString.length);
//     }
//     if (cookieString.indexOf(cookieName + '=') == 0) {
//       return cookieString.substring(cookieName.length + 1, cookieString.length);
//     }
//   }

//   return undefined;
// };

const baseQuery = fetchBaseQuery({
  baseUrl: baseUrl,
  credentials: 'include',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).user.access_token;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

const baseQueryWithIntercept: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result: QueryReturnValue<unknown, FetchBaseQueryError, FetchBaseQueryMeta> =
    await baseQuery(args, api, extraOptions);
  const { data, error } = result;
  // 401 handle
  if (error && error.status === 401) {
    console.debug('try to refresh token');
    const { user } = api.getState() as RootState;
    const { access_token, refresh_token } = user;

    // send refresh token request
    if (access_token && refresh_token) {
      const refreshResult: QueryReturnValue<any> = await baseQuery(
        {
          url: '/api/v1/auth/refresh',
          method: 'POST',
          body: {
            access_token,
            refresh_token,
          },
        },
        api,
        extraOptions,
      );
      if (refreshResult.data) {
        // update token
        const { access_token } = refreshResult.data.data;
        api.dispatch(refreshToken(access_token));

        // TODO, clear cache
        api.dispatch(baseApi.util.resetApiState())

        // retry the initial query
        result = await baseQuery(args, api, extraOptions)
      } else {
        api.dispatch(userLogout());
      }
    } else {
      api.dispatch(userLogout());
    }
  }

  // other error status handle
  if (error) {
    // fetch error or server timeout
    if (error.status === 'FETCH_ERROR' || error.status === 'TIMEOUT_ERROR') {
      console.error('Network error or server timeout:', error);
      message.error('Network error, please check your connection or try again later.');
      return Promise.reject('Network error or server timeout');
    }

    // const { status } = error as FetchBaseQueryError;
    const errorData = error.data as IResponseError;
    // console.log(errorData)
    // handleReqError(Number(status), url, errorData.errorMessage);

    console.log(errorData);
    // type of error.message is Error422
    let errorMsg = '';
    if (errorData.errorMessage instanceof Array) {
      const error422 = errorData.errorMessage[0];
      errorMsg = error422.msg;
    } else {
      errorMsg = errorData.errorMessage as string;
    }

    return Promise.reject(errorMsg);
  }
  // success
  const { success, errorMessage } = data as IResponseSuccess;
  if (success) {
    return result;
  } else {
    if (result) return result;
    throw new TypeError(errorMessage);
  }
};

export const baseApi = createApi({
  baseQuery: baseQueryWithIntercept,
  reducerPath: 'baseApi',
  // 缓存时间，以秒为单位，默认是60秒
  // keepUnusedDataFor: 2 * 60,
  // refetchOnMountOrArgChange: 30 * 60,
  tagTypes: [
    'Auth',
    'Account',
    'APIAccount',
    'Job',
    'Template'
  ],
  endpoints: () => ({}),
});
