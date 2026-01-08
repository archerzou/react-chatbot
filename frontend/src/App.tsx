import React from 'react';
import { MantineProvider, Container, Stack, Box, Loader, Center, Text, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';
import { AppProvider, useApp } from './context/AppContext';
import Header from './components/Header';
import SearchPanel from './components/SearchPanel';
import DataTable from './components/DataTable';
import ReportPreview from './components/ReportPreview';

const theme = createTheme({
  primaryColor: 'pink',
  colors: {
    pink: [
      '#fce4ec',
      '#f8bbd9',
      '#f48fb1',
      '#f06292',
      '#ec407a',
      '#E91E63',
      '#d81b60',
      '#c2185b',
      '#ad1457',
      '#880e4f',
    ],
    cyan: [
      '#e0f7fa',
      '#b2ebf2',
      '#80deea',
      '#4dd0e1',
      '#26c6da',
      '#00bcd4',
      '#0099D8',
      '#0097a7',
      '#00838f',
      '#006064',
    ],
  },
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
});

const AppContent: React.FC = () => {
  const { loading } = useApp();

  if (loading) {
    return (
      <Center style={{ height: '100vh' }}>
        <Stack align="center" gap="md">
          <Loader size="xl" color="pink" />
          <Text c="dimmed">Loading...</Text>
        </Stack>
      </Center>
    );
  }

  return (
    <Box style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <Header />
      <Container size="xl" py="md">
        <Stack gap="md">
          <SearchPanel />
          <DataTable />
          <ReportPreview />
        </Stack>
      </Container>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <MantineProvider theme={theme}>
      <Notifications position="top-right" />
      <AppProvider>
        <AppContent />
      </AppProvider>
    </MantineProvider>
  );
};

export default App;
