// import React, { useContext, useState } from 'react';
import { LogoutOutlined } from '@ant-design/icons';
import { Dropdown, Space, Avatar } from 'antd';
import type { MenuProps } from 'antd'
// import { SettingsContext, ThemeName } from '@/providers/Setting.provider';
import useCurrentUser from '@/hooks/useCurrentUser';

export const UserMenu: React.FC = () => {
  const currentUser = useCurrentUser();

  const items: MenuProps['items'] = [
    {
      key: 'email',
      type: 'group',
      label: 'Email',
      children: [
        {
          key: 'email-show',
          label: currentUser.data && currentUser.data.email,
          disabled: true,
        },
      ],
    },
    {
      key: 'role',
      type: 'group',
      label: 'Role',
      children: [
        {
          key: 'role-show',
          label: (currentUser.data && currentUser.data.role.name) || '',
          disabled: true,
        },
      ],
    },
    // {
    //     key: 'Setting',
    //     label: t('user.setting'),
    //     icon: <SettingOutlined />,
    // },
    // {
    //   key: 'SignOut',
    //   label: 'SignOut',
    //   danger: true,
    //   icon: <LogoutOutlined />,
    // },
  ];

  // open user setting modal
  // const [isModalOpened, setIsModalOpened] = useState(false);

  const handleClickMenu = (e: any) => {
    switch (e.key) {
      case 'Setting':
        // setIsModalOpened(true);
        break;

      default:
        break;
    }
  };

  // const handleModalOk = () => {
  //   setIsModalOpened(false);
  // };

  // const handleModalCancel = () => {
  //   setIsModalOpened(false);
  // };

  // user theme config
  // const { themeName, setTheme } = useContext(SettingsContext);

  // const onThemeChange = (value: ThemeName) => {
  //   setTheme(value);
  // };

  return (
    <div
      key="UserProfile"
      aria-hidden
      style={{
        display: 'flex',
        alignItems: 'center',
      }}
      onMouseDown={(e) => {
        e.stopPropagation();
        e.preventDefault();
      }}
    >
      <Dropdown
        menu={{
          items: items,
          onClick: handleClickMenu,
        }}
      >
        <Space size="small">
          <Avatar style={{ verticalAlign: 'middle' }}>
            {currentUser.data && currentUser.data.username}
          </Avatar>
        </Space>
      </Dropdown>
    </div >
  );
};
