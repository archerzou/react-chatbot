import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserInfo, ClientSearchResult, ReportData, SearchFilters } from '../types';
import { fetchUserInfo, searchClients, getReportData, downloadPdf, logout as apiLogout } from '../api/chatApi';

interface AppContextType {
  userInfo: UserInfo | null;
  searchResults: ClientSearchResult[];
  selectedClient: ClientSearchResult | null;
  reportData: ReportData | null;
  loading: boolean;
  searchLoading: boolean;
  reportLoading: boolean;
  hasSearched: boolean;
  error: string | null;
  search: (filters: SearchFilters) => Promise<void>;
  selectClient: (client: ClientSearchResult | null) => void;
  loadReportData: (clientId: string) => Promise<void>;
  downloadReport: (clientId: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  clearResults: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [searchResults, setSearchResults] = useState<ClientSearchResult[]>([]);
  const [selectedClient, setSelectedClient] = useState<ClientSearchResult | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchLoading, setSearchLoading] = useState<boolean>(false);
  const [reportLoading, setReportLoading] = useState<boolean>(false);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUserInfo = async () => {
      try {
        const info = await fetchUserInfo();
        setUserInfo(info);
      } catch (err) {
        console.error('Failed to load user info:', err);
        setError('Failed to load user information');
      } finally {
        setLoading(false);
      }
    };

    loadUserInfo();
  }, []);

  const search = async (filters: SearchFilters) => {
    setSearchLoading(true);
    setError(null);
    setSelectedClient(null);
    setReportData(null);

    try {
      const response = await searchClients(filters);
      setSearchResults(response.results);
      setHasSearched(true);
    } catch (err: any) {
      console.error('Search error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to search clients';
      setError(errorMessage);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const selectClient = (client: ClientSearchResult | null) => {
    setSelectedClient(client);
    setReportData(null);
  };

  const loadReportData = async (clientId: string) => {
    setReportLoading(true);
    setError(null);

    try {
      const data = await getReportData(clientId);
      setReportData(data);
    } catch (err: any) {
      console.error('Report data error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to load report data';
      setError(errorMessage);
    } finally {
      setReportLoading(false);
    }
  };

  const downloadReport = async (clientId: string) => {
    setError(null);

    try {
      const blob = await downloadPdf(clientId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const clientName = selectedClient?.client_name?.replace(/\s+/g, '_') || 'unknown';
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      link.download = `client_report_${clientName}_${date}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Download error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to download PDF';
      setError(errorMessage);
    }
  };

  const logout = () => {
    setUserInfo(null);
    setSearchResults([]);
    setSelectedClient(null);
    setReportData(null);
    apiLogout();
  };

  const clearError = () => setError(null);

  const clearResults = () => {
    setSearchResults([]);
    setSelectedClient(null);
    setReportData(null);
    setHasSearched(false);
  };

  return (
    <AppContext.Provider
      value={{
        userInfo,
        searchResults,
        selectedClient,
        reportData,
        loading,
        searchLoading,
        reportLoading,
        hasSearched,
        error,
        search,
        selectClient,
        loadReportData,
        downloadReport,
        logout,
        clearError,
        clearResults,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
