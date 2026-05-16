import { Copy } from 'lucide-react';
import { motion } from 'framer-motion';
import type { RegressionScenario } from '../../types';

interface ScenarioCardProps {
  scenario: RegressionScenario;
  index: number;
}

export const ScenarioCard = ({ scenario, index }: ScenarioCardProps) => {
  const handleCopy = () => {
    const testCode = generateTestCode(scenario);
    navigator.clipboard.writeText(testCode);
  };

  const generateTestCode = (scenario: RegressionScenario) => {
    return `it('${scenario.title}', async () => {
  // ${scenario.description}
  const result = await ${scenario.affected_component}({
    status: 'PROCESSING',
    ...testData
  });
  
  expect(result).resolves.toBeDefined();
  // ${scenario.expected_behavior}
});`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="card p-6 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-sm font-semibold text-prism-text flex-1">
          {scenario.title}
        </h3>
        <button
          onClick={handleCopy}
          className="p-2 hover:bg-prism-bg rounded transition-colors"
          title="Copy test code"
        >
          <Copy className="w-4 h-4 text-prism-text-muted" />
        </button>
      </div>

      {/* Code Block */}
      <div className="bg-prism-bg rounded p-4 mb-4 font-mono text-xs overflow-x-auto flex-1">
        <pre className="text-prism-text-muted">
          <span className="text-prism-blue">it</span>
          <span className="text-prism-text">(</span>
          <span className="text-prism-orange">'{scenario.title}'</span>
          <span className="text-prism-text">, </span>
          <span className="text-prism-blue">async</span>
          <span className="text-prism-text"> () {'=>'} {'{'}</span>
          {'\n  '}
          <span className="text-prism-text-muted">// {scenario.description}</span>
          {'\n  '}
          <span className="text-prism-blue">const</span>
          <span className="text-prism-text"> result = </span>
          <span className="text-prism-blue">await</span>
          <span className="text-prism-text"> </span>
          <span className="text-prism-green">{scenario.affected_component}</span>
          <span className="text-prism-text">({'{'}</span>
          {'\n    '}
          <span className="text-prism-text">status: </span>
          <span className="text-prism-orange">'PROCESSING'</span>
          <span className="text-prism-text">,</span>
          {'\n    '}
          <span className="text-prism-text">...testData</span>
          {'\n  '}
          <span className="text-prism-text">{'}'});</span>
          {'\n  '}
          <span className="text-prism-blue">expect</span>
          <span className="text-prism-text">(result).</span>
          <span className="text-prism-green">resolves</span>
          <span className="text-prism-text">.toBeDefined();</span>
          {'\n'}<span className="text-prism-text">{'}'});</span>
        </pre>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs px-2 py-1 rounded bg-prism-orange/10 text-prism-orange border border-prism-orange/30 font-mono">
          #{scenario.affected_component.split('.')[0]}
        </span>
        <span className="text-xs px-2 py-1 rounded bg-prism-blue/10 text-prism-blue border border-prism-blue/30 font-mono">
          #regression
        </span>
        <span className="text-xs px-2 py-1 rounded bg-prism-yellow/10 text-prism-yellow border border-prism-yellow/30 font-mono">
          #{scenario.priority.toLowerCase()}
        </span>
      </div>
    </motion.div>
  );
};

// Made with Bob
