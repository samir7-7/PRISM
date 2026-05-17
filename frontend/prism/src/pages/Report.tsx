import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAnalysisStore } from '../store/analysisStore';
import { Dashboard } from './Dashboard';
import type { ReportResponse, AnalyzeResponse } from '../types';

export const Report = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setAnalysis, setLoading, setError } = useAnalysisStore();
  const [isLoadingReport, setIsLoadingReport] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    const loadReport = async () => {
      if (!id) {
        setLoadError('No report ID provided');
        setIsLoadingReport(false);
        return;
      }

      setLoading(true);
      setIsLoadingReport(true);
      setLoadError(null);

      try {
        // Accept both string and numeric IDs
        const report = await apiService.getReport(id);
        
        // Convert ReportResponse to AnalyzeResponse format
        const analysisData: AnalyzeResponse = {
          report_id: report.id,
          pr_id: report.pr_id,
          repository: report.repository,
          pr_url: report.pr_url,
          changed_files: report.changed_files,
          impacted_nodes: report.impacted_nodes,
          risk_score: report.risk_score,
          risk_level: report.risk_level,
          risk_factors: report.risk_factors,
          semantic_insights: report.semantic_insights,
          regression_scenarios: report.regression_scenarios,
          analysis_duration: report.analysis_duration || 0,
          created_at: report.created_at,
        };

        setAnalysis(analysisData);
        setIsLoadingReport(false);
        setLoading(false);
      } catch (error: any) {
        console.error('Failed to load report:', error);
        const errorMessage = error.response?.data?.detail || 'Failed to load report';
        setError(errorMessage);
        setLoadError(errorMessage);
        setIsLoadingReport(false);
        setLoading(false);
      }
    };

    loadReport();
  }, [id, setAnalysis, setLoading, setError]);

  if (isLoadingReport) {
    return (
      <div className="min-h-screen bg-prism-bg flex items-center justify-center">
        <div className="text-prism-text-muted">Loading report...</div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
        <div className="card p-8 max-w-md text-center">
          <h2 className="text-2xl font-bold text-prism-red mb-4">Report Not Found</h2>
          <p className="text-prism-text-muted mb-6">{loadError}</p>
          <p className="text-sm text-prism-text-muted mb-6">
            Report ID: <code className="bg-prism-bg px-2 py-1 rounded">{id}</code>
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-prism-blue hover:bg-prism-blue/80 text-white font-medium px-6 py-2 rounded transition-colors"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return <Dashboard />;
};

// Made with Bob
