import React from 'react';
import { Paper, Title, Text, Group, Stack, Divider, Button, Grid, Box, Alert, Loader, Center } from '@mantine/core';
import { Download, AlertCircle, Home, Heart, Brain } from 'lucide-react';
import { useApp } from '../context/AppContext';

const safeStr = (value: string | null | undefined): string => {
  if (value === null || value === undefined) return 'Not available';
  return String(value);
};

const ReportPreview: React.FC = () => {
  const { reportData, reportLoading, selectedClient, downloadReport, error } = useApp();

  if (!selectedClient) {
    return null;
  }

  if (reportLoading) {
    return (
      <Paper shadow="xs" p="xl" withBorder>
        <Center>
          <Stack align="center" gap="md">
            <Loader size="lg" />
            <Text>Loading report data...</Text>
          </Stack>
        </Center>
      </Paper>
    );
  }

  if (!reportData) {
    return null;
  }

  const handleDownload = async () => {
    await downloadReport(reportData.koo_clientid);
  };

  const hasHousingConcerns = reportData.housing_concerns === 1;
  const hasDisabilityConcerns = reportData.is_disability_discussed === 1;
  const hasMentalHealthConcerns = reportData.mmh_concerns === 1 || reportData.family_mental_concerns === 1;

  return (
    <Paper shadow="xs" p="md" withBorder>
      <Stack gap="md">
        <Group justify="space-between" align="center">
          <Title order={4} c="cyan.7">CLIENT BACKGROUND REPORT</Title>
          <Button
            leftSection={<Download size={16} />}
            onClick={handleDownload}
            variant="filled"
          >
            Download PDF
          </Button>
        </Group>
        
        <Text size="sm" c="dimmed">Based on Plunket AI Model Analysis</Text>
        
        <Divider />

        {error && (
          <Alert icon={<AlertCircle size={16} />} color="red" variant="light">
            {error}
          </Alert>
        )}

        <Box>
          <Title order={5} c="cyan.7" mb="sm">CLIENT INFORMATION</Title>
          <Grid>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Client Name</Text>
              <Text fw={500}>{safeStr(reportData.client_name)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Client NHI</Text>
              <Text fw={500}>{safeStr(reportData.client_nhi)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">DHB</Text>
              <Text fw={500}>{safeStr(reportData.dhb)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Ethnicity</Text>
              <Text fw={500}>{safeStr(reportData.ethnicity)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Domicile</Text>
              <Text fw={500}>{safeStr(reportData.domicile)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Gender</Text>
              <Text fw={500}>{safeStr(reportData.gender)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Primary Caregiver</Text>
              <Text fw={500}>{safeStr(reportData.primary_caregiver)}</Text>
            </Grid.Col>
            <Grid.Col span={6}>
              <Text size="sm" c="dimmed">Well Child Level of Need</Text>
              <Text fw={500}>{safeStr(reportData.well_child_level_of_need)}</Text>
            </Grid.Col>
          </Grid>
        </Box>

        <Divider />

        {hasHousingConcerns && (
          <>
            <Box>
              <Group gap="xs" mb="sm">
                <Home size={18} color="#0099D8" />
                <Title order={5} c="cyan.7">HOUSING RISK</Title>
              </Group>
              <Text size="sm">
                <Text span fw={500}>Risk Categories: </Text>
                {safeStr(reportData.housing_risk_categories)}
              </Text>
            </Box>
            <Divider />
          </>
        )}

        {hasDisabilityConcerns && (
          <>
            <Box>
              <Group gap="xs" mb="sm">
                <Heart size={18} color="#0099D8" />
                <Title order={5} c="cyan.7">DISABILITY CONCERN</Title>
              </Group>
              <Text size="sm">
                <Text span fw={500}>Disability Categories: </Text>
                {safeStr(reportData.disability_categories)}
              </Text>
              <Text size="sm" mt="xs">
                <Text span fw={500}>Family Member Disability: </Text>
                {safeStr(reportData.family_member_disability)}
              </Text>
            </Box>
            <Divider />
          </>
        )}

        {hasMentalHealthConcerns && (
          <>
            <Box>
              <Group gap="xs" mb="sm">
                <Brain size={18} color="#0099D8" />
                <Title order={5} c="cyan.7">MENTAL HEALTH CONCERN</Title>
              </Group>
              {reportData.mmh_concerns === 1 && (
                <Text size="sm">
                  <Text span fw={500}>Mental Health Categories: </Text>
                  {safeStr(reportData.mental_health_categories)}
                </Text>
              )}
              {reportData.family_mental_concerns === 1 && (
                <Text size="sm" mt="xs">
                  <Text span fw={500}>Family Mental Health Categories: </Text>
                  {safeStr(reportData.family_mental_health_categories)}
                </Text>
              )}
              {reportData.family_member_impact && (
                <Text size="sm" mt="xs">
                  <Text span fw={500}>Family Member Impact: </Text>
                  {safeStr(reportData.family_member_impact)}
                </Text>
              )}
            </Box>
            <Divider />
          </>
        )}

        <Box>
          <Title order={5} c="cyan.7" mb="sm">SUMMARIES</Title>
          
          <Text fw={500} size="sm" mt="md">Housing Summary</Text>
          <Text size="sm" c="dimmed">{safeStr(reportData.house_summary)}</Text>
          
          <Text fw={500} size="sm" mt="md">IMPA Summary</Text>
          <Text size="sm" c="dimmed">{safeStr(reportData.impa_summary)}</Text>
          
          <Text fw={500} size="sm" mt="md">MMH Summary</Text>
          <Text size="sm" c="dimmed">{safeStr(reportData.mmh_summary)}</Text>
        </Box>

        <Divider />

        <Text size="xs" c="dimmed" ta="right">
          Generated by Plunket AI Model
        </Text>
      </Stack>
    </Paper>
  );
};

export default ReportPreview;
