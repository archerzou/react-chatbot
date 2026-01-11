import React, { useState, useEffect } from 'react';
import { Paper, Table, Radio, Button, Group, Text, ScrollArea, Stack, Alert, Pagination } from '@mantine/core';
import { FileText, AlertCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { ClientSearchResult } from '../types';
import NotFound from './NotFound';

const PAGE_SIZE = 10;

const DataTable: React.FC = () => {
  const { 
    searchResults, 
    selectedClient, 
    selectClient, 
    loadReportData, 
    reportLoading,
    hasSearched,
    error 
  } = useApp();

  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchResults]);

  const totalPages = Math.ceil(searchResults.length / PAGE_SIZE);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedResults = searchResults.slice(startIndex, startIndex + PAGE_SIZE);

  const handleRowSelect = (client: ClientSearchResult) => {
    selectClient(client);
  };

  const handleGenerateReport = async () => {
    if (selectedClient) {
      await loadReportData(selectedClient.koo_clientid);
    }
  };

  if (searchResults.length === 0 && hasSearched) {
    return <NotFound />;
  }

  if (searchResults.length === 0) {
    return null;
  }

  return (
    <Paper shadow="xs" p="md" withBorder>
      <Stack gap="md">
        <Group justify="space-between">
          <Text fw={500} size="lg">Search Results</Text>
          <Button
            leftSection={<FileText size={16} />}
            onClick={handleGenerateReport}
            loading={reportLoading}
            disabled={!selectedClient}
          >
            Generate Report
          </Button>
        </Group>

        {error && (
          <Alert icon={<AlertCircle size={16} />} color="red" variant="light">
            {error}
          </Alert>
        )}

        <ScrollArea>
          <Table striped highlightOnHover withTableBorder withColumnBorders>
            <Table.Thead>
              <Table.Tr>
                <Table.Th style={{ width: 50 }}>Select</Table.Th>
                <Table.Th>Client Name</Table.Th>
                <Table.Th>NHI</Table.Th>
                <Table.Th>Date</Table.Th>
                <Table.Th>Housing</Table.Th>
                <Table.Th>IMPA</Table.Th>
                <Table.Th>MMH</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {paginatedResults.map((client, index) => (
                <Table.Tr 
                  key={`${client.koo_clientid}-${startIndex + index}`}
                  style={{ 
                    cursor: 'pointer',
                    backgroundColor: selectedClient?.koo_clientid === client.koo_clientid 
                      ? 'var(--mantine-color-blue-light)' 
                      : undefined
                  }}
                  onClick={() => handleRowSelect(client)}
                >
                  <Table.Td>
                    <Radio
                      checked={selectedClient?.koo_clientid === client.koo_clientid}
                      onChange={() => handleRowSelect(client)}
                    />
                  </Table.Td>
                  <Table.Td>{client.client_name}</Table.Td>
                  <Table.Td>{client.client_nhi || '-'}</Table.Td>
                  <Table.Td>{client.create_date || '-'}</Table.Td>
                  <Table.Td>
                    <Text size="sm" lineClamp={1}>
                      {client.response_house ? 'Yes' : '-'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" lineClamp={1}>
                      {client.response_impa ? 'Yes' : '-'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" lineClamp={1}>
                      {client.response_mmh ? 'Yes' : '-'}
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </ScrollArea>

        {searchResults.length > PAGE_SIZE && (
          <Group justify="flex-end">
            <Pagination
              total={totalPages}
              value={currentPage}
              onChange={setCurrentPage}
            />
          </Group>
        )}
      </Stack>
    </Paper>
  );
};

export default DataTable;
