import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';

interface AIInsightCardProps {
  insights: string;
}

export const AIInsightCard = ({ insights }: AIInsightCardProps) => {
  // Extract hashtags from insights
  const extractHashtags = (text: string): string[] => {
    const hashtagRegex = /#[\w-]+/g;
    return text.match(hashtagRegex) || [];
  };

  const hashtags = extractHashtags(insights);
  const cleanInsights = insights.replace(/#[\w-]+/g, '').trim();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="card p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Bot className="w-5 h-5 text-prism-blue" />
          <h3 className="text-sm font-semibold text-prism-text">AI Analysis</h3>
        </div>
        <span className="badge-info">AI INSIGHT</span>
      </div>

      {/* Content */}
      <div className="text-sm text-prism-text-muted leading-relaxed mb-4">
        {cleanInsights || insights}
      </div>

      {/* Tags */}
      {hashtags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {hashtags.map((tag, index) => (
            <span
              key={index}
              className="text-xs px-2 py-1 rounded bg-prism-blue/10 text-prism-blue border border-prism-blue/30 font-mono"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
};

// Made with Bob
