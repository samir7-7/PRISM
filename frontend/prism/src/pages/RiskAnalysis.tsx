import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Bot, TrendingUp, Shield, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { TopNav } from '../components/layout/TopNav';
import { Sidebar } from '../components/layout/Sidebar';
import { RiskBadge } from '../components/dashboard/RiskBadge';
import { MarkdownRenderer } from '../components/common/MarkdownRenderer';
import { useAnalysisStore } from '../store/analysisStore';
import type { RegressionScenario } from '../types';

export const RiskAnalysis = () => {
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
        <div className="flex flex-col items-center gap-4">
          <div className="skeleton w-16 h-16 rounded-full"></div>
          <div className="text-body text-prism-text-muted">Loading analysis...</div>
        </div>
      </div>
    );
  }

  // Extract hashtags from insights
  const extractHashtags = (text: string): string[] => {
    const hashtagRegex = /#[\w-]+/g;
    return text.match(hashtagRegex) || [];
  };

  const hashtags = extractHashtags(currentAnalysis.semantic_insights);
  const cleanInsights = currentAnalysis.semantic_insights.replace(/#[\w-]+/g, '').trim();

  // Group scenarios by priority
  const groupedScenarios = {
    HIGH: currentAnalysis.regression_scenarios.filter(s => s.priority === 'HIGH'),
    MEDIUM: currentAnalysis.regression_scenarios.filter(s => s.priority === 'MEDIUM'),
    LOW: currentAnalysis.regression_scenarios.filter(s => s.priority === 'LOW'),
  };

  const totalRisks = currentAnalysis.regression_scenarios.length;
  const criticalCount = groupedScenarios.HIGH.length;
  const warningCount = groupedScenarios.MEDIUM.length;
  const advisoryCount = groupedScenarios.LOW.length;

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col">
      <TopNav />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        
        <main className="flex-1 p-6 overflow-auto custom-scrollbar">
          {/* Breadcrumb */}
          <div className="text-overline text-prism-text-muted mb-4">
            ANALYSIS {'>'} RISK INTELLIGENCE
          </div>

          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
            <div>
              <h1 className="text-h1 text-prism-text mb-2">Risk Analysis</h1>
              <p className="text-body text-prism-text-muted">
                AI-powered risk detection and semantic analysis
              </p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-prism-red/10 border border-prism-red/30">
              <div className="status-dot-error status-dot-pulse"></div>
              <span className="text-body-sm text-prism-red font-semibold">
                {criticalCount} CRITICAL RISKS DETECTED
              </span>
            </div>
          </div>

          {/* Risk Overview Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="text-overline text-prism-text-muted">TOTAL RISKS</div>
                <AlertTriangle className="w-5 h-5 text-prism-orange" />
              </div>
              <div className="text-h1 text-prism-text">{totalRisks}</div>
              <div className="text-caption text-prism-text-muted mt-1">Identified issues</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="text-overline text-prism-text-muted">CRITICAL</div>
                <Shield className="w-5 h-5 text-prism-red" />
              </div>
              <div className="text-h1 text-prism-red">{criticalCount}</div>
              <div className="text-caption text-prism-text-muted mt-1">High priority</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="text-overline text-prism-text-muted">WARNING</div>
                <TrendingUp className="w-5 h-5 text-prism-yellow" />
              </div>
              <div className="text-h1 text-prism-yellow">{warningCount}</div>
              <div className="text-caption text-prism-text-muted mt-1">Medium priority</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="text-overline text-prism-text-muted">ADVISORY</div>
                <Bot className="w-5 h-5 text-prism-blue" />
              </div>
              <div className="text-h1 text-prism-blue">{advisoryCount}</div>
              <div className="text-caption text-prism-text-muted mt-1">Low priority</div>
            </motion.div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* AI Semantic Analysis - 2 columns */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="lg:col-span-2 card p-6"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Bot className="w-6 h-6 text-prism-blue" />
                  <div>
                    <h2 className="text-h4 text-prism-text">AI Semantic Analysis</h2>
                    <p className="text-caption text-prism-text-muted mt-1">
                      Deep learning insights from code changes
                    </p>
                  </div>
                </div>
                <span className="badge badge-info">AI POWERED</span>
              </div>

              {/* AI Insights Content */}
              <div className="mb-6">
                <MarkdownRenderer content={cleanInsights || currentAnalysis.semantic_insights} />
              </div>

              {/* Tags */}
              {hashtags.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-4 border-t border-prism-border">
                  {hashtags.map((tag, index) => (
                    <span
                      key={index}
                      className="text-caption px-2.5 py-1 rounded bg-prism-blue/10 text-prism-blue border border-prism-blue/30 font-mono"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Risk Score */}
              <div className="mt-6 pt-6 border-t border-prism-border">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-overline text-prism-text-muted mb-2">OVERALL RISK SCORE</div>
                    <div className="flex items-baseline gap-3">
                      <span className="text-h1 text-prism-orange">{Math.round(currentAnalysis.risk_score)}</span>
                      <span className="text-body text-prism-text-muted">/ 100</span>
                      <span className={`badge ${
                        currentAnalysis.risk_level === 'CRITICAL' ? 'badge-critical' :
                        currentAnalysis.risk_level === 'HIGH' ? 'badge-warning' :
                        'badge-advisory'
                      }`}>
                        {currentAnalysis.risk_level}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => navigate('/dashboard/tests')}
                    className="btn-primary flex items-center gap-2"
                  >
                    View Test Scenarios
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Detected Risks List - 1 column */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="card p-6"
            >
              {/* Header */}
              <div className="flex items-center gap-3 mb-6">
                <AlertTriangle className="w-6 h-6 text-prism-orange" />
                <div>
                  <h2 className="text-h4 text-prism-text">Detected Risks</h2>
                  <p className="text-caption text-prism-text-muted mt-1">
                    {totalRisks} issues identified
                  </p>
                </div>
              </div>

              {/* Risk List */}
              <div className="space-y-4 max-h-[600px] overflow-y-auto custom-scrollbar">
                {/* Critical Risks */}
                {groupedScenarios.HIGH.map((scenario) => (
                  <div key={scenario.scenario_id} className="border-l-2 border-prism-red pl-3 py-2">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="text-body-sm font-semibold text-prism-text">{scenario.title}</h4>
                      <RiskBadge priority="HIGH" />
                    </div>
                    <p className="text-caption text-prism-text-muted leading-relaxed mb-2">
                      {scenario.description}
                    </p>
                    <div className="text-caption text-prism-text-muted font-mono">
                      {scenario.affected_component}
                    </div>
                  </div>
                ))}

                {/* Warning Risks */}
                {groupedScenarios.MEDIUM.map((scenario) => (
                  <div key={scenario.scenario_id} className="border-l-2 border-prism-yellow pl-3 py-2">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="text-body-sm font-semibold text-prism-text">{scenario.title}</h4>
                      <RiskBadge priority="MEDIUM" />
                    </div>
                    <p className="text-caption text-prism-text-muted leading-relaxed mb-2">
                      {scenario.description}
                    </p>
                    <div className="text-caption text-prism-text-muted font-mono">
                      {scenario.affected_component}
                    </div>
                  </div>
                ))}

                {/* Advisory Risks */}
                {groupedScenarios.LOW.map((scenario) => (
                  <div key={scenario.scenario_id} className="border-l-2 border-prism-blue pl-3 py-2">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="text-body-sm font-semibold text-prism-text">{scenario.title}</h4>
                      <RiskBadge priority="LOW" />
                    </div>
                    <p className="text-caption text-prism-text-muted leading-relaxed mb-2">
                      {scenario.description}
                    </p>
                    <div className="text-caption text-prism-text-muted font-mono">
                      {scenario.affected_component}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Made with Bob