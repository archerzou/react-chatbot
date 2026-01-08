import React from 'react';
import { Avatar, Menu, Text, UnstyledButton } from '@mantine/core';
import { LogOut } from 'lucide-react';
import { useApp } from '../context/AppContext';

const UserMenu: React.FC = () => {
  const { userInfo, logout } = useApp();

  const handleLogout = () => {
    try {
      logout();
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  const getInitial = () => {
    if (userInfo?.username) {
      return userInfo.username.charAt(0).toUpperCase();
    }
    return 'U';
  };

  return (
    <Menu shadow="md" width={200} position="bottom-end">
        <Menu.Target>
          <UnstyledButton>
            <Avatar color="indigo" radius="xl" size="sm">
              {getInitial()}
            </Avatar>
          </UnstyledButton>
        </Menu.Target>

        <Menu.Dropdown>
          <Menu.Label>
            <Text size="sm" fw={500}>{userInfo?.username || 'Loading...'}</Text>
            <Text size="xs" c="dimmed">{userInfo?.email || 'Loading...'}</Text>
          </Menu.Label>
          <Menu.Divider />
          <Menu.Item leftSection={<LogOut size={14} />} onClick={handleLogout}>
            Log out
          </Menu.Item>
        </Menu.Dropdown>
    </Menu>
  );
};

export default UserMenu;         