import axios from 'axios';
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  ReportResponse,
  ReportListResponse,
  StatsResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export const apiService = {
  /**
   * Analyze a pull request
   * POST /api/analyze
   */
  analyzePR: async (data: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await api.post<AnalyzeResponse>('/api/analyze', data);
    return response.data;
  },

  /**
   * Get a specific report by ID (string or number)
   * GET /api/reports/{report_id}
   */
  getReport: async (reportId: string | number): Promise<ReportResponse> => {
    const response = await api.get<ReportResponse>(`/api/reports/${reportId}`);
    return response.data;
  },

  /**
   * Get report by PR ID and repository
   * GET /api/reports/pr/{pr_id}?repository=...
   */
  getReportByPR: async (prId: string, repository: string): Promise<ReportResponse> => {
    const response = await api.get<ReportResponse>(`/api/reports/pr/${prId}`, {
      params: { repository },
    });
    return response.data;
  },

  /**
   * List all reports with pagination
   * GET /api/reports
   */
  listReports: async (page = 1, pageSize = 50): Promise<ReportListResponse> => {
    const response = await api.get<ReportListResponse>('/api/reports', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Get summary statistics
   * GET /api/reports/stats/summary
   */
  getStats: async (): Promise<StatsResponse> => {
    const response = await api.get<StatsResponse>('/api/reports/stats/summary');
    return response.data;
  },

  /**
   * Health check
   * GET /health
   */
  checkHealth: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default apiService;

// Made with Bob
