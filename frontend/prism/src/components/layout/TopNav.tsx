import { Bell, Settings } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAnalysisStore } from '../../store/analysisStore';

export const TopNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { clearAnalysis } = useAnalysisStore();

  const tabs = [
    { name: 'GRAPH', path: '/dashboard' },
    { name: 'RISK ANALYSIS', path: '/dashboard/risk-analysis' },
    { name: 'TESTS', path: '/dashboard/tests' },
  ];

  const handleReAnalyze = () => {
    clearAnalysis();
    navigate('/');
  };

  return (
    <nav className="bg-prism-surface border-b border-prism-border px-6 py-4 sticky top-0 z-40">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <h1
            className="text-h3 font-mono text-prism-text cursor-pointer hover:text-prism-blue transition-colors"
            onClick={() => {
              // Navigate to dashboard if on a dashboard route, otherwise go home
              if (location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/report')) {
                navigate('/dashboard');
              } else {
                navigate('/');
              }
            }}
          >
            PRISM
          </h1>

          {/* Tabs */}
          <div className="hidden md:flex gap-6">
            {tabs.map((tab) => (
              <button
                key={tab.path}
                onClick={() => navigate(tab.path)}
                className={`text-overline transition-colors relative pb-1 focus-ring ${
                  location.pathname === tab.path
                    ? 'text-prism-text'
                    : 'text-prism-text-muted hover:text-prism-text'
                }`}
              >
                {tab.name}
                {location.pathname === tab.path && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-prism-blue rounded-full"></div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button className="btn-ghost p-2" title="Notifications">
            <Bell className="w-5 h-5" />
          </button>
          <button className="btn-ghost p-2" title="Settings">
            <Settings className="w-5 h-5" />
          </button>
          <button
            onClick={handleReAnalyze}
            className="btn-primary btn-sm hidden sm:flex"
          >
            RE-ANALYZE
          </button>
        </div>
      </div>
    </nav>
  );
};

// Made with Bob
