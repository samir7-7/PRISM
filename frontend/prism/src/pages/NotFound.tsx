import { useNavigate } from 'react-router-dom';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
      <div className="card p-8 max-w-md text-center">
        <h1 className="text-6xl font-bold text-prism-blue mb-4">404</h1>
        <h2 className="text-2xl font-bold text-prism-text mb-4">Page Not Found</h2>
        <p className="text-prism-text-muted mb-6">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="bg-prism-card hover:bg-prism-card/80 text-prism-text font-medium px-6 py-2 rounded transition-colors border border-prism-border"
          >
            Go Back
          </button>
          <button
            onClick={() => navigate('/')}
            className="bg-prism-blue hover:bg-prism-blue/80 text-white font-medium px-6 py-2 rounded transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Made with Bob