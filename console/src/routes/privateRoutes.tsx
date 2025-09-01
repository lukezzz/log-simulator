import { MainLayout } from '@/components/Layout';
import { RoleEnum } from '@/data/SiteData';
import { Jobs } from '@/pages/Jobs';
import { AdminLoginForm } from '@/pages/Login';
import LogParserPage from '@/pages/LogParserPage';
import { Templates } from '@/pages/Templates';
import type { RouteObject } from 'react-router-dom';


// Asynchronously load components
const loadError404 = async () => {
  const { Error404 } = await import('@/components/error/404');
  return { Component: Error404 };
};

export const privateRoutes = (role: RoleEnum | undefined) => {

  let routes: RouteObject[] = [
    {
      path: '*',
      async lazy() {
        return loadError404();
      },
    },
  ]

  if (!role) {
    return {
      path: '/',
      children: [
        {
          path: '/login',
          element: <AdminLoginForm />
        },
        // {
        //   path: '/admin/login',
        //   element: <AdminLoginForm />
        // },
        {
          path: '/',
          element: <AdminLoginForm />
        },
        { path: '*', element: <AdminLoginForm /> }
      ],
    }
  }

  if (role === RoleEnum.admin) {
    routes = [
      {
        path: '/',
        element: <Jobs />,
        children: [
          { path: '*', element: <Jobs /> }
        ],
      },
      {
        path: '/jobs',
        element: <Jobs />,
        children: [
          { path: '*', element: <Jobs /> }
        ],
      },
      {
        path: '/templates',
        children: [
          { path: '*', index: true, element: <Templates /> }
        ],
      },
      {
        path: '/tools/parser',
        element: <LogParserPage />,
        children: [
          { path: '*', element: <LogParserPage /> }
        ],
      }
    ]
  }


  // if (role === RoleEnum.guest) {
  //   routes = [
  //     {
  //       path: '/Home',
  //       element: <GuestHome />,
  //       children: [
  //         { path: '*', element: <GuestHome /> }
  //       ],
  //     },
  //     { path: '*', element: <GuestHome /> },
  //     { path: '', element: <Navigate to="/Home" replace /> }
  //   ]
  // }

  return {
    path: '/',
    element: <MainLayout />,
    children: routes
  }
};
