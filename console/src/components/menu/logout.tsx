// import React, { useContext, useState } from 'react';
import { LogoutOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { useLogoutMutation } from '@/services/auth';
// import { SettingsContext, ThemeName } from '@/providers/Setting.provider';
import { useDispatch } from 'react-redux';
import { baseApi } from '@/services/base';
import { userLogout } from '@/redux/reducers/userSlice';

export const LogoutBtn: React.FC = () => {

  const dispatch = useDispatch();

  // user signout
  const [logout] = useLogoutMutation();

  // open user setting modal
  // const [isModalOpened, setIsModalOpened] = useState(false);

  const handleLogout = () => {
    logout();
    // dispatch(baseApi.util.resetApiState());
    // dispatch(userLogout());
  };


  return (
    <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout} danger></Button>
  );
};
