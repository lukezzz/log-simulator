import {
  ContainerOutlined,
  FileSearchOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import React from 'react';
import { RoleEnum } from './SiteData';

export interface ISiteItem {
  exact?: boolean;
  icon: React.JSX.Element | string;
  locale: string;
  name: React.JSX.Element | string;
  path: string;
  hideInMenu?: boolean;
  hideChildrenInMenu?: boolean;
  breadcrumbName?: string;
  authority: RoleEnum[];
  // sub menu
  routes?: ISiteRoute['routes'];
}

export interface ISiteRoute {
  path: string;
  routes: Array<ISiteItem>;
}

const siteRoutes: ISiteRoute = {
  path: '/',
  routes: [
    {
      name: 'Jobs',
      locale: 'Jobs',
      path: '/jobs',
      authority: [RoleEnum.admin],
      exact: true,
      hideInMenu: false,
      icon: <ContainerOutlined />,
    },
    {
      name: 'Templates',
      locale: 'Templates',
      path: '/templates',
      authority: [RoleEnum.admin],
      exact: true,
      hideInMenu: false,
      icon: <DatabaseOutlined />,
    },
    {
      name: 'Log Parser',
      locale: 'Log Parser',
      path: '/tools/parser',
      authority: [RoleEnum.admin],
      exact: true,
      hideInMenu: false,
      icon: <FileSearchOutlined />,
    },
  ],
};

export const appList = [];

export default siteRoutes;
