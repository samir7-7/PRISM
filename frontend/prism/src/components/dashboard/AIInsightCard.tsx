import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import { MarkdownRenderer } from '../common/MarkdownRenderer';

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
          <h3 className="text-h5 text-prism-text">AI Analysis</h3>
        </div>
        <span className="badge badge-info">AI INSIGHT</span>
      </div>

      {/* Content with Markdown Support */}
      <div className="mb-4">
        <MarkdownRenderer content={cleanInsights || insights} />
      </div>

      {/* Tags */}
      {hashtags.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-3 border-t border-prism-border">
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
    </motion.div>
  );
};

// Made with Bob
