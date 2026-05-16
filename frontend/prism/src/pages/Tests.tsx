import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Info, ExternalLink, MoreVertical } from 'lucide-react';
import { motion } from 'framer-motion';
import { TopNav } from '../components/layout/TopNav';
import { Sidebar } from '../components/layout/Sidebar';
import { ScenarioCard } from '../components/tests/ScenarioCard';
import { useAnalysisStore } from '../store/analysisStore';

export const Tests = () => {
  const navigate = useNavigate();
  const { currentAnalysis, isLoading } = useAnalysisStore();

  useEffect(() => {
    if (!currentAnalysis && !isLoading) {
      navigate('/');
    }
  }, [currentAnalysis, isLoading, navigate]);

  if (!currentAnalysis) {
    return (
      <div className="min-h-screen bg-prism-bg flex items-center justify-center">
        <div className="text-prism-text-muted">Loading...</div>
      </div>
    );
  }

  const criticalCount = currentAnalysis.regression_scenarios.filter(
    s => s.priority === 'HIGH'
  ).length;

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col">
      <TopNav />
      
      <div className="flex flex-1">
        <Sidebar />
        
        <main className="flex-1 p-6 overflow-auto">
          {/* Breadcrumb */}
          <div className="text-xs text-prism-text-muted mb-4 font-mono">
            TEST SUITE {'>'} REGRESSIONS
          </div>

          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-prism-text">
              Regression Scenarios
            </h1>
            <div className="flex items-center gap-2 px-3 py-2 rounded bg-prism-red/10 border border-prism-red/30">
              <div className="w-2 h-2 rounded-full bg-prism-red animate-pulse"></div>
              <span className="text-sm text-prism-red font-medium">
                {criticalCount} CRITICAL PATHS DETECTED
              </span>
            </div>
          </div>

          {/* Scenarios Panel */}
          <div className="card p-6 mb-6">
            {/* Panel Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-prism-blue" />
                  <h2 className="text-sm font-semibold text-prism-text">
                    Generated Regression Scenarios
                  </h2>
                </div>
                <div className="text-sm text-prism-green">
                  Coverage: +12.4%
                </div>
              </div>
              <button className="p-2 hover:bg-prism-bg rounded transition-colors">
                <MoreVertical className="w-5 h-5 text-prism-text-muted" />
              </button>
            </div>

            {/* Scenario Grid */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              {currentAnalysis.regression_scenarios.map((scenario, index) => (
                <ScenarioCard
                  key={scenario.scenario_id}
                  scenario={scenario}
                  index={index}
                />
              ))}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-prism-border">
              <div className="flex items-center gap-2 text-xs text-prism-text-muted">
                <Info className="w-4 h-4" />
                <span>
                  Scenarios are inferred from AST modifications in{' '}
                  <span className="text-prism-text font-mono">
                    {currentAnalysis.changed_files[0] || 'modified files'}
                  </span>
                </span>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-prism-blue hover:bg-prism-blue/80 text-white rounded text-sm font-medium transition-colors">
                Append to Test Suite
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card p-6"
            >
              <div className="text-xs text-prism-text-muted uppercase tracking-wider mb-2">
                IMPACT SCORE
              </div>
              <div className="text-3xl font-bold text-prism-text">
                {Math.round(currentAnalysis.risk_score)}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card p-6"
            >
              <div className="text-xs text-prism-text-muted uppercase tracking-wider mb-2">
                NEW VECTORS
              </div>
              <div className="text-3xl font-bold text-prism-green">
                {currentAnalysis.regression_scenarios.length}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
              <div className="text-xs text-prism-text-muted uppercase tracking-wider mb-2">
                RISK MITIGATION
              </div>
              <div className="text-3xl font-bold text-prism-yellow">
                {currentAnalysis.risk_level}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card p-6"
            >
              <div className="text-xs text-prism-text-muted uppercase tracking-wider mb-2">
                COVERAGE DEBT
              </div>
              <div className="text-3xl font-bold text-prism-red">
                +{(100 - currentAnalysis.risk_factors.test_coverage).toFixed(1)}%
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Made with Bob
