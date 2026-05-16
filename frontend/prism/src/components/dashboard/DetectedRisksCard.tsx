import { AlertTriangle, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { RiskBadge } from './RiskBadge';
import type { RegressionScenario } from '../../types';

interface DetectedRisksCardProps {
  scenarios: RegressionScenario[];
}

export const DetectedRisksCard = ({ scenarios }: DetectedRisksCardProps) => {
  const navigate = useNavigate();

  // Group scenarios by priority
  const groupedScenarios = {
    HIGH: scenarios.filter(s => s.priority === 'HIGH'),
    MEDIUM: scenarios.filter(s => s.priority === 'MEDIUM'),
    LOW: scenarios.filter(s => s.priority === 'LOW'),
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="card p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <AlertTriangle className="w-5 h-5 text-prism-orange" />
        <h3 className="text-sm font-semibold text-prism-text">Detected Risks</h3>
      </div>

      {/* Risk List */}
      <div className="space-y-4 mb-4">
        {/* Critical Risks */}
        {groupedScenarios.HIGH.map((scenario, index) => (
          <div key={scenario.scenario_id} className="border-l-2 border-prism-red pl-3">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="text-sm font-semibold text-prism-text">{scenario.title}</h4>
              <RiskBadge priority="HIGH" />
            </div>
            <p className="text-xs text-prism-text-muted">{scenario.description}</p>
          </div>
        ))}

        {/* Warning Risks */}
        {groupedScenarios.MEDIUM.map((scenario, index) => (
          <div key={scenario.scenario_id} className="border-l-2 border-prism-yellow pl-3">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="text-sm font-semibold text-prism-text">{scenario.title}</h4>
              <RiskBadge priority="MEDIUM" />
            </div>
            <p className="text-xs text-prism-text-muted">{scenario.description}</p>
          </div>
        ))}

        {/* Advisory Risks */}
        {groupedScenarios.LOW.slice(0, 2).map((scenario, index) => (
          <div key={scenario.scenario_id} className="border-l-2 border-prism-blue pl-3">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="text-sm font-semibold text-prism-text">{scenario.title}</h4>
              <RiskBadge priority="LOW" />
            </div>
            <p className="text-xs text-prism-text-muted">{scenario.description}</p>
          </div>
        ))}
      </div>

      {/* Footer Link */}
      <button
        onClick={() => navigate('/dashboard/tests')}
        className="text-sm text-prism-blue hover:text-prism-blue/80 flex items-center gap-2 transition-colors"
      >
        VIEW ALL {scenarios.length} ANOMALIES
        <ArrowRight className="w-4 h-4" />
      </button>
    </motion.div>
  );
};

// Made with Bob
