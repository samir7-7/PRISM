import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAnalysisStore } from '../store/analysisStore';
import { Dashboard } from './Dashboard';
import type { ReportResponse } from '../types';

export const Report = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setAnalysis, setLoading, setError } = useAnalysisStore();
  const [isLoadingReport, setIsLoadingReport] = useState(true);

  useEffect(() => {
    const loadReport = async () => {
      if (!id) {
        navigate('/');
        return;
      }

      setLoading(true);
      setIsLoadingReport(true);

      try {
        const report = await apiService.getReport(parseInt(id));
        
        // Convert ReportResponse to AnalyzeResponse format
        const analysisData = {
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

        setAnalysis(analysisData as any);
        setIsLoadingReport(false);
        setLoading(false);
      } catch (error: any) {
        console.error('Failed to load report:', error);
        setError(error.response?.data?.detail || 'Failed to load report');
        setIsLoadingReport(false);
        setLoading(false);
        navigate('/');
      }
    };

    loadReport();
  }, [id, navigate, setAnalysis, setLoading, setError]);

  if (isLoadingReport) {
    return (
      <div className="min-h-screen bg-prism-bg flex items-center justify-center">
        <div className="text-prism-text-muted">Loading report...</div>
      </div>
    );
  }

  return <Dashboard />;
};

// Made with Bob
