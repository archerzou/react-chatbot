import axios from 'axios';
import { UserInfo, SearchResponse, ReportData, SearchFilters } from '../types';

export const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchUserInfo = async (): Promise<UserInfo> => {
  try {
    const response = await api.get('/login');
    return response.data.user_info;
  } catch (error) {
    console.error('Error fetching user info:', error);
    throw error;
  }
};

export const logout = () => {
  window.location.href = `${API_URL}/logout`;
};

export const searchClients = async (filters: SearchFilters): Promise<SearchResponse> => {
  try {
    const payload: Record<string, string | null> = {
      client_name: filters.client_name || null,
      client_nhi: filters.client_nhi || null,
      start_date: filters.start_date ? filters.start_date.toISOString().split('T')[0] : null,
      end_date: filters.end_date ? filters.end_date.toISOString().split('T')[0] : null,
    };
    
    const response = await api.post('/search', payload);
    return response.data;
  } catch (error) {
    console.error('Error searching clients:', error);
    throw error;
  }
};

export const getReportData = async (clientId: string): Promise<ReportData> => {
  try {
    const response = await api.get(`/report/${encodeURIComponent(clientId)}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching report data:', error);
    throw error;
  }
};

export const downloadPdf = async (clientId: string): Promise<Blob> => {
  try {
    const response = await api.get(`/report/${encodeURIComponent(clientId)}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error downloading PDF:', error);
    throw error;
  }
};
