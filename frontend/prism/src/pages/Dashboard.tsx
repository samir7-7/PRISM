import { useEffect } from 'react';
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

  useEffect(() => {
    // Redirect to home if no analysis data
    if (!currentAnalysis && !isLoading) {
      navigate('/');
    }
  }, [currentAnalysis, isLoading, navigate]);

  if (!currentAnalysis) {
    return (
      <div className="min-h-screen bg-prism-bg flex items-center justify-center">
        <div className="text-prism-text-muted">Loading analysis...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col">
      <TopNav />
      
      <div className="flex flex-1">
        <Sidebar />
        
        <main className="flex-1 p-6 overflow-auto">
          {/* Stats Row */}
          <StatsRow
            impactedNodes={currentAnalysis.impacted_nodes.length}
            regressionScenarios={currentAnalysis.regression_scenarios.length}
            analysisDuration={currentAnalysis.analysis_duration}
          />

          {/* Main Content Grid */}
          <div className="grid grid-cols-3 gap-6">
            {/* Left Panel - Dependency Graph (2 columns) */}
            <div className="col-span-2">
              <DependencyGraph
                impactedNodes={currentAnalysis.impacted_nodes}
                changedFiles={currentAnalysis.changed_files}
              />
            </div>

            {/* Right Panel - AI Insights & Risks (1 column) */}
            <div className="space-y-6">
              <AIInsightCard insights={currentAnalysis.semantic_insights} />
              <DetectedRisksCard scenarios={currentAnalysis.regression_scenarios} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Made with Bob
