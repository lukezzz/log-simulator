import { RoleEnum } from '@/data/SiteData';

interface Role {
  name: RoleEnum;
}

export interface UserFormProps {
  displayName?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
}

type UserBase = {
  username: string;
  email: string;
  display_name?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role: Role;
};

export type UserProps = UserBase & {
  id: string;
  remember?: boolean;
  desc?: string;
};

export interface UserResponse {
  data: UserProps;
}

export interface UserState {
  data: UserProps | undefined
  isSessionTimeout: boolean;
  isAuthenticating: boolean;
  access_token: string | undefined;
  refresh_token: string | undefined;
}

type UserRolePermissionsProps = {
  id: number;
  name: string;
};

export interface UserRoleProps {
  id: number;
  name: string;
  permissions: UserRolePermissionsProps[];
}
