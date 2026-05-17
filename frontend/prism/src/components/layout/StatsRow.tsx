import { motion } from 'framer-motion';

interface StatCardProps {
  label: string;
  value: string | number;
  valueColor?: string;
  delay?: number;
}

const StatCard = ({ label, value, valueColor = 'text-prism-text', delay = 0 }: StatCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="card p-6 hover:shadow-lg transition-shadow"
  >
    <div className="text-overline text-prism-text-muted mb-3">
      {label}
    </div>
    <div className={`text-h2 ${valueColor}`}>
      {value}
    </div>
  </motion.div>
);

interface StatsRowProps {
  impactedNodes: number;
  regressionScenarios: number;
  analysisDuration: number;
}

export const StatsRow = ({
  impactedNodes,
  regressionScenarios,
  analysisDuration
}: StatsRowProps) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <StatCard
        label="IMPACTED NODES"
        value={`${impactedNodes} Components`}
        delay={0.1}
      />
      <StatCard
        label="REGRESSION SCENARIOS"
        value={`${regressionScenarios} Generated`}
        delay={0.2}
      />
      <StatCard
        label="ANALYSIS TIME"
        value={`${analysisDuration.toFixed(1)}s`}
        valueColor="text-prism-green"
        delay={0.3}
      />
    </div>
  );
};

// Made with Bob
