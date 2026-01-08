import React, { useState } from 'react';
import { Paper, TextInput, Button, Group, Stack, Text } from '@mantine/core';
import { Search, X } from 'lucide-react';
import { useApp } from '../context/AppContext';

interface LocalFilters {
  client_name: string;
  client_nhi: string;
  start_date: string;
  end_date: string;
}

const SearchPanel: React.FC = () => {
  const { search, searchLoading, searchResults, clearResults, clearError } = useApp();
  
  const [filters, setFilters] = useState<LocalFilters>({
    client_name: '',
    client_nhi: '',
    start_date: '',
    end_date: '',
  });

  const handleSearch = async () => {
    clearError();
    const searchFilters = {
      client_name: filters.client_name,
      client_nhi: filters.client_nhi,
      start_date: filters.start_date ? new Date(filters.start_date) : null,
      end_date: filters.end_date ? new Date(filters.end_date) : null,
    };
    await search(searchFilters);
  };

  const handleClear = () => {
    setFilters({
      client_name: '',
      client_nhi: '',
      start_date: '',
      end_date: '',
    });
    clearResults();
    clearError();
  };

  const hasFilters = filters.client_name || filters.client_nhi || filters.start_date || filters.end_date;

  return (
    <Paper shadow="xs" p="md" withBorder>
      <Stack gap="md">
        <Text fw={500} size="lg">Search Clients</Text>
        
        <Group grow>
          <TextInput
            label="Client Name"
            placeholder="Enter client name (partial match)"
            value={filters.client_name}
            onChange={(e) => setFilters({ ...filters, client_name: e.target.value })}
          />
          <TextInput
            label="Client NHI"
            placeholder="Enter NHI number (partial match)"
            value={filters.client_nhi}
            onChange={(e) => setFilters({ ...filters, client_nhi: e.target.value })}
          />
        </Group>
        
        <Group grow>
          <TextInput
            label="Start Date"
            placeholder="YYYY-MM-DD"
            type="date"
            value={filters.start_date}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
          />
          <TextInput
            label="End Date"
            placeholder="YYYY-MM-DD"
            type="date"
            value={filters.end_date}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
          />
        </Group>
        
        <Group justify="space-between">
          <Text size="sm" c="dimmed">
            {searchResults.length > 0 && `Found ${searchResults.length} record(s)`}
          </Text>
          <Group>
            {hasFilters && (
              <Button
                variant="subtle"
                leftSection={<X size={16} />}
                onClick={handleClear}
              >
                Clear
              </Button>
            )}
            <Button
              leftSection={<Search size={16} />}
              onClick={handleSearch}
              loading={searchLoading}
              disabled={!hasFilters}
            >
              Search
            </Button>
          </Group>
        </Group>
      </Stack>
    </Paper>
  );
};

export default SearchPanel;
