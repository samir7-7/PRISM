import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface TerminalWindowProps {
  prId: string;
  repository: string;
  reportId?: number;
  riskScore?: number;
  riskLevel?: string;
  impactedNodes?: number;
  semanticRisks?: number;
  onComplete?: () => void;
}

export const TerminalWindow = ({
  prId,
  repository,
  reportId,
  riskScore,
  riskLevel,
  impactedNodes = 14,
  semanticRisks = 3,
  onComplete,
}: TerminalWindowProps) => {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const steps = [
    { icon: '✅', text: 'Pull request analyzed', delay: 500 },
    { icon: '✅', text: 'Dependency graph constructed', delay: 800 },
    { icon: '✅', text: `${impactedNodes} impacted nodes identified`, delay: 1000 },
    { icon: '⚠️', text: `${semanticRisks} semantic risks detected`, delay: 1200 },
    { icon: '✅', text: 'Regression scenarios generated', delay: 1500 },
  ];

  useEffect(() => {
    if (currentStep < steps.length) {
      const timer = setTimeout(() => {
        setCurrentStep(currentStep + 1);
      }, steps[currentStep].delay);
      return () => clearTimeout(timer);
    } else if (onComplete) {
      setTimeout(onComplete, 500);
    }
  }, [currentStep, steps.length, onComplete]);

  const getRiskColor = (level?: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return 'text-prism-red';
      case 'HIGH':
        return 'text-prism-orange';
      case 'MEDIUM':
        return 'text-prism-yellow';
      case 'LOW':
        return 'text-prism-green';
      default:
        return 'text-prism-text';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card overflow-hidden"
      >
        {/* Terminal Header */}
        <div className="bg-prism-surface border-b border-prism-border px-4 py-3 flex items-center gap-2">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-prism-red"></div>
            <div className="w-3 h-3 rounded-full bg-prism-yellow"></div>
            <div className="w-3 h-3 rounded-full bg-prism-green"></div>
          </div>
          <span className="ml-4 text-prism-text-muted text-sm font-mono">
            prism-cli --analyze
          </span>
        </div>

        {/* Terminal Content */}
        <div className="bg-prism-bg p-6 font-mono text-sm">
          {/* Command */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4"
          >
            <span className="text-prism-green">$</span>{' '}
            <span className="text-prism-text">
              prism analyze pull-request --id={prId} --repository={repository} --verbose
            </span>
          </motion.div>

          {/* Status Lines */}
          <div className="space-y-2 mb-6">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{
                  opacity: currentStep > index ? 1 : 0,
                  x: currentStep > index ? 0 : -10,
                }}
                className="flex items-center gap-2"
              >
                <span>{step.icon}</span>
                <span className="text-prism-text-muted">{step.text}</span>
              </motion.div>
            ))}
          </div>

          {/* Analysis Summary */}
          {currentStep >= steps.length && riskScore !== undefined && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="space-y-4"
            >
              <div className="border-t border-prism-border pt-4">
                <div className="text-prism-text-muted mb-2">ANALYSIS SUMMARY</div>
                <div className="flex items-baseline gap-2">
                  <span className="text-prism-text">Risk Score:</span>
                  <span className={`text-2xl font-bold ${getRiskColor(riskLevel)}`}>
                    {riskLevel?.toUpperCase()}
                  </span>
                  <span className="text-prism-text-muted">
                    ({Math.round(riskScore)}/100)
                  </span>
                </div>
              </div>

              {reportId && (
                <div className="bg-prism-red/10 border border-prism-red/30 rounded p-4">
                  <div className="text-prism-text-muted text-xs mb-2">
                    Open full analysis:
                  </div>
                  <a
                    href={`/report/${reportId}`}
                    onClick={(e) => {
                      e.preventDefault();
                      navigate(`/report/${reportId}`);
                    }}
                    className="text-prism-blue hover:text-prism-blue/80 flex items-center gap-2 break-all"
                  >
                    {window.location.origin}/report/{reportId}
                    <ExternalLink className="w-4 h-4 flex-shrink-0" />
                  </a>
                </div>
              )}

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="flex items-center gap-2 text-prism-green"
              >
                <span className="animate-pulse">_</span>
                <span>Ready for review. Analysis complete.</span>
              </motion.div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

// Made with Bob
