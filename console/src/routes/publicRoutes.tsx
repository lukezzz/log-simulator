// import { UserLoginForm } from '@/pages/Login';

import { AdminLoginForm } from "@/pages/Login";

export const publicRoutes = (currentUser) => {

  console.log(currentUser)

  return [
    {
      path: '/',
      element: <AdminLoginForm />,
      children: [
        // { path: '*', element: <UserLoginForm /> }
      ],
    },
    {
      path: '/admin/login',
      element: <AdminLoginForm />,
      children: [
        // { path: '*', element: <UserLoginForm /> }
      ],
    },
    // {
    //   path: '/login',
    //   element: <UserLoginForm />,
    //   children: [
    //     // { path: '*', element: <UserLoginForm /> }
    //   ],
    // },

    { path: '*', element: <AdminLoginForm /> },
    // { path: '*', element: <Navigate to="/login" /> },
  ];
};
