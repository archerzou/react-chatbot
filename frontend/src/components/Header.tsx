import React from 'react';
import { Title, Text, Group, Paper, Image } from '@mantine/core';
import UserMenu from './UserMenu';

const Header: React.FC = () => {
  return (
    <Paper 
      shadow="xs" 
      p="md" 
      style={{ 
        borderBottom: '1px solid #dee2e6',
        borderRadius: 0,
      }}
    >
      <Group justify="space-between" align="center">
        <Group gap="md">
          <Image
            src="/logo.png"
            alt="Healthcare Report Logo"
            h={50}
            w="auto"
            fit="contain"
          />
          <div>
            <Title order={4} style={{ margin: 0 }}>Healthcare Report</Title>
            <Text size="sm" c="dimmed">Search for client records and generate reports</Text>
          </div>
        </Group>
        <UserMenu />
      </Group>
    </Paper>
  );
};

export default Header;      