import React from 'react';
import { Paper, Text, Stack, Center } from '@mantine/core';
import { SearchX } from 'lucide-react';

interface NotFoundProps {
  message?: string;
  description?: string;
}

const NotFound: React.FC<NotFoundProps> = ({
  message = 'No client records found.',
  description = 'Please refine your search criteria.',
}) => {
  return (
    <Paper shadow="xs" p="xl" withBorder>
      <Center>
        <Stack align="center" gap="md">
          <SearchX size={48} color="var(--mantine-color-gray-5)" />
          <Stack align="center" gap="xs">
            <Text fw={500} size="lg" c="dimmed">
              {message}
            </Text>
            <Text size="sm" c="dimmed">
              {description}
            </Text>
          </Stack>
        </Stack>
      </Center>
    </Paper>
  );
};

export default NotFound;
