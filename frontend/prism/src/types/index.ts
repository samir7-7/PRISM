// API Types based on backend schemas

export interface RiskFactors {
  complexity_score: number;
  impact_scope: number;
  criticality: number;
  test_coverage: number;
}

export interface RegressionScenario {
  scenario_id: string;
  title: string;
  description: string;
  affected_component: string;
  test_steps: string[];
  expected_behavior: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

// Legacy endpoint request (POST /api/analyze) - deprecated
export interface AnalyzeRequest {
  pr_id: string;
  repository: string;
}

// CLI contract types (POST /api/analysis/run) - canonical endpoint
export interface AnalysisRunRequest {
  pr_identifier: string;
  repository_url: string;
  github_token?: string;
}

export interface AnalysisRunResponse {
  report_id: string;
  dashboard_url: string;
  risk_score: number;
  risk_label: 'LOW' | 'MEDIUM' | 'HIGH';
  impacted_node_count: number;
  status: 'COMPLETE' | 'PARTIAL';
}

export interface AnalyzeResponse {
  report_id: string;
  pr_id: string;
  repository: string;
  pr_url?: string;
  changed_files: string[];
  impacted_nodes: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_factors: RiskFactors;
  semantic_insights: string;
  regression_scenarios: RegressionScenario[];
  analysis_duration: number;
  created_at: string;
}

export interface ReportResponse {
  id: number;
  report_id?: string;
  pr_id: string;
  repository: string;
  pr_url?: string;
  changed_files: string[];
  dependency_graph: any;
  impacted_nodes: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_factors: RiskFactors;
  semantic_insights: string;
  regression_scenarios: RegressionScenario[];
  created_at: string;
  analysis_duration?: number;
  status: string;
  error_message?: string;
}

export interface ReportListItem {
  id: number;
  report_id?: string;
  pr_id: string;
  repository: string;
  risk_score: number;
  risk_level: string;
  created_at: string;
  status: string;
}

export interface ReportListResponse {
  reports: ReportListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface StatsResponse {
  total_reports: number;
  avg_risk_score: number;
  high_risk_count: number;
  recent_analyses: number;
}

// Graph Node Types
export interface GraphNode {
  id: string;
  type: 'source' | 'impacted' | 'nominal';
  data: {
    label: string;
    service: string;
    method: string;
    status: string;
  };
  position: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
}

// UI State Types
export interface AnalysisState {
  currentAnalysis: AnalyzeResponse | null;
  isLoading: boolean;
  error: string | null;
  setAnalysis: (analysis: AnalyzeResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearAnalysis: () => void;
}

// Made with Bob
