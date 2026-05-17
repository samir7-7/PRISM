import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { TerminalWindow } from '../components/cli/TerminalWindow';
import { apiService } from '../services/api';
import { useAnalysisStore } from '../store/analysisStore';

export const CLISplash = () => {
  const navigate = useNavigate();
  const { setAnalysis, setLoading, setError } = useAnalysisStore();
  const [prId, setPrId] = useState('');
  const [repository, setRepository] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prId || !repository) return;

    setIsAnalyzing(true);
    setLoading(true);

    try {
      const result = await apiService.analyzePR({ pr_id: prId, repository });
      setAnalysisData(result);
      setAnalysis(result);
      setAnalysisComplete(true);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to analyze PR');
      setIsAnalyzing(false);
      setLoading(false);
    }
  };

  const handleViewDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 className="text-display font-mono text-prism-text mb-4">
          PRISM
        </h1>
        <p className="text-body-lg text-prism-text-muted">
          Predictive Risk Intelligence & Semantic Monitoring
        </p>
      </motion.div>

      {/* Input Form or Terminal */}
      {!isAnalyzing ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <form onSubmit={handleAnalyze} className="card p-8 space-y-6">
            <div>
              <label className="label">
                Pull Request ID
              </label>
              <input
                type="text"
                value={prId}
                onChange={(e) => setPrId(e.target.value)}
                placeholder="e.g., 123"
                className="input focus-ring"
                required
              />
            </div>

            <div>
              <label className="label">
                Repository
              </label>
              <input
                type="text"
                value={repository}
                onChange={(e) => setRepository(e.target.value)}
                placeholder="e.g., owner/repo"
                className="input focus-ring"
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary btn-lg w-full flex items-center justify-center gap-2"
            >
              Analyze Pull Request
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
        </motion.div>
      ) : (
        <>
          <TerminalWindow
            prId={prId}
            repository={repository}
            reportId={analysisData?.report_id}
            riskScore={analysisData?.risk_score}
            riskLevel={analysisData?.risk_level}
            impactedNodes={analysisData?.impacted_nodes?.length}
            semanticRisks={analysisData?.regression_scenarios?.filter(
              (s: any) => s.priority === 'HIGH'
            ).length}
            onComplete={() => setLoading(false)}
          />

          {analysisComplete && (
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              onClick={handleViewDashboard}
              className="mt-8 bg-prism-blue hover:bg-prism-blue/80 text-white font-medium px-8 py-3 rounded transition-colors flex items-center gap-2"
            >
              View Dashboard
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          )}
        </>
      )}

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="absolute bottom-8 left-8 right-8 flex justify-between items-center text-xs text-prism-text-muted font-mono"
      >
        <div>PRISM-ENGINE-V4.2.1 / ENVIRONMENT: PRODUCTION</div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-prism-green animate-pulse"></div>
          <span>All systems nominal</span>
          <span className="text-prism-green">128ms latency</span>
        </div>
      </motion.div>
    </div>
  );
};

// Made with Bob
