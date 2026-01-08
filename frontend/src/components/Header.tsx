import React from 'react';
import { Box, Title, Text, Group, Paper } from '@mantine/core';
import { FileText } from 'lucide-react';
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
          <Box
            style={{
              width: 40,
              height: 40,
              backgroundColor: '#E91E63',
              borderRadius: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <FileText size={20} color="white" />
          </Box>
          <div>
            <Title order={4} style={{ margin: 0 }}>Healthcare Dashboard</Title>
            <Text size="sm" c="dimmed">Search for client records and generate reports</Text>
          </div>
        </Group>
        <UserMenu />
      </Group>
    </Paper>
  );
};

export default Header;   