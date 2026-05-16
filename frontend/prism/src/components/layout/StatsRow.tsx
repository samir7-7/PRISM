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
    className="card p-6"
  >
    <div className="text-xs text-prism-text-muted uppercase tracking-wider mb-2">
      {label}
    </div>
    <div className={`text-3xl font-bold ${valueColor}`}>
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
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard
        label="IMPACTED NODES"
        value={`${impactedNodes} COMPONENTS AFFECTED`}
        delay={0.1}
      />
      <StatCard
        label="REGRESSION SCENARIOS"
        value={`${regressionScenarios} GENERATED`}
        delay={0.2}
      />
      <StatCard
        label="ANALYSIS TIME"
        value={`${analysisDuration.toFixed(1)}s DURATION`}
        valueColor="text-prism-green"
        delay={0.3}
      />
    </div>
  );
};

// Made with Bob
