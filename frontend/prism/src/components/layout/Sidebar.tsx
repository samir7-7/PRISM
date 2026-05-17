import { 
  LayoutDashboard, 
  GitBranch, 
  AlertTriangle, 
  FlaskConical, 
  FileText,
  BookOpen,
  HelpCircle
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAnalysisStore } from '../../store/analysisStore';

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentAnalysis } = useAnalysisStore();

  const navItems = [
    { icon: GitBranch, label: 'DEPENDENCY GRAPH', path: '/dashboard', enabled: true },
    { icon: AlertTriangle, label: 'RISK ANALYSIS', path: '/dashboard/risk-analysis', enabled: true },
    { icon: FlaskConical, label: 'TEST SCENARIOS', path: '/dashboard/tests', enabled: true },
  ];

  const bottomItems = [
    { icon: BookOpen, label: 'DOCUMENTATION', path: '#' },
    { icon: HelpCircle, label: 'SUPPORT', path: '#' },
  ];

  return (
    <aside className="w-64 bg-prism-surface border-r border-prism-border flex flex-col">
      {/* PR Info */}
      {currentAnalysis && (
        <div className="p-4 border-b border-prism-border">
          <div className="text-overline text-prism-text-muted mb-2">PULL REQUEST</div>
          <div className="text-body font-mono text-prism-text font-semibold">
            #{currentAnalysis.pr_id}
          </div>
          <div className="text-caption text-prism-text-muted mt-1 truncate" title={currentAnalysis.repository}>
            {currentAnalysis.repository}
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto custom-scrollbar">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <button
                key={item.path}
                onClick={() => item.enabled && navigate(item.path)}
                disabled={!item.enabled}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded text-body-sm transition-all focus-ring ${
                  !item.enabled
                    ? 'text-prism-text-muted/50 cursor-not-allowed opacity-60'
                    : isActive
                    ? 'bg-prism-blue/20 text-prism-blue font-semibold'
                    : 'text-prism-text-muted hover:text-prism-text hover:bg-prism-bg'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="font-medium tracking-wide">{item.label}</span>
                {!item.enabled && (
                  <span className="ml-auto text-caption text-prism-text-muted/50">Soon</span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Bottom Navigation */}
      <div className="p-4 border-t border-prism-border space-y-1">
        {bottomItems.map((item) => {
          const Icon = item.icon;
          
          return (
            <button
              key={item.label}
              onClick={() => item.path !== '#' && navigate(item.path)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded text-body-sm text-prism-text-muted hover:text-prism-text hover:bg-prism-bg transition-all focus-ring"
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium tracking-wide">{item.label}</span>
            </button>
          );
        })}
      </div>
    </aside>
  );
};

// Made with Bob
