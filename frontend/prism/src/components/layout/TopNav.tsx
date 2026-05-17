import { Bell, Settings } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAnalysisStore } from '../../store/analysisStore';

export const TopNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { clearAnalysis } = useAnalysisStore();

  const tabs = [
    { name: 'EXPLORER', path: '/dashboard' },
    { name: 'TIMELINE', path: '/dashboard/timeline' },
    { name: 'IMPACT', path: '/dashboard/impact' },
  ];

  const handleReAnalyze = () => {
    clearAnalysis();
    navigate('/');
  };

  return (
    <nav className="bg-prism-surface border-b border-prism-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <h1
            className="text-2xl font-bold font-mono text-prism-text cursor-pointer"
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
          <div className="flex gap-6">
            {tabs.map((tab) => (
              <button
                key={tab.path}
                onClick={() => navigate(tab.path)}
                className={`text-sm font-medium tracking-wider transition-colors relative pb-1 ${
                  location.pathname === tab.path
                    ? 'text-prism-text'
                    : 'text-prism-text-muted hover:text-prism-text'
                }`}
              >
                {tab.name}
                {location.pathname === tab.path && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-prism-blue"></div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-prism-bg rounded transition-colors">
            <Bell className="w-5 h-5 text-prism-text-muted" />
          </button>
          <button className="p-2 hover:bg-prism-bg rounded transition-colors">
            <Settings className="w-5 h-5 text-prism-text-muted" />
          </button>
          <button
            onClick={handleReAnalyze}
            className="bg-prism-blue hover:bg-prism-blue/80 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
          >
            RE-ANALYZE
          </button>
        </div>
      </div>
    </nav>
  );
};

// Made with Bob
