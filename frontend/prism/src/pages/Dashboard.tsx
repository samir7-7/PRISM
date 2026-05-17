import { useNavigate } from 'react-router-dom';
import { TopNav } from '../components/layout/TopNav';
import { Sidebar } from '../components/layout/Sidebar';
import { StatsRow } from '../components/layout/StatsRow';
import { DependencyGraph } from '../components/dashboard/DependencyGraph';
import { AIInsightCard } from '../components/dashboard/AIInsightCard';
import { DetectedRisksCard } from '../components/dashboard/DetectedRisksCard';
import { useAnalysisStore } from '../store/analysisStore';

export const Dashboard = () => {
  const navigate = useNavigate();
  const { currentAnalysis, isLoading } = useAnalysisStore();

  // Show message if no analysis data instead of redirecting
  if (!currentAnalysis && !isLoading) {
    return (
      <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
        <div className="card p-8 max-w-md text-center animate-fade-in">
          <h2 className="text-h2 text-prism-text mb-4">No Analysis Data</h2>
          <p className="text-body text-prism-text-muted mb-6">
            Please run an analysis first to view the dashboard.
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary btn-lg"
          >
            Run Analysis
          </button>
        </div>
      </div>
    );
  }

  if (isLoading || !currentAnalysis) {
    return (
      <div className="min-h-screen bg-prism-bg flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="skeleton w-16 h-16 rounded-full"></div>
          <div className="text-body text-prism-text-muted">Loading analysis...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col">
      <TopNav />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="p-6 pb-0">
            {/* Breadcrumb */}
            <div className="text-overline text-prism-text-muted mb-4">
              ANALYSIS {'>'} DEPENDENCY GRAPH
            </div>

            {/* Header */}
            <div className="mb-6">
              <h1 className="text-h1 text-prism-text mb-2">Dependency Graph</h1>
              <p className="text-body text-prism-text-muted">
                Visual representation of code dependencies and impact analysis
              </p>
            </div>

            {/* Stats Row */}
            <StatsRow
              impactedNodes={currentAnalysis.impacted_nodes.length}
              regressionScenarios={currentAnalysis.regression_scenarios.length}
              analysisDuration={currentAnalysis.analysis_duration}
            />
          </div>

          {/* Full-Width Dependency Graph */}
          <div className="flex-1 p-6 pt-0">
            <DependencyGraph
              impactedNodes={currentAnalysis.impacted_nodes}
              changedFiles={currentAnalysis.changed_files}
            />
          </div>
        </main>
      </div>
    </div>
  );
};

// Made with Bob
