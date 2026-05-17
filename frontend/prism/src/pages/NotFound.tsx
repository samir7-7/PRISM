import { useNavigate } from 'react-router-dom';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
      <div className="card p-8 max-w-md text-center animate-fade-in">
        <h1 className="text-display text-prism-blue mb-4">404</h1>
        <h2 className="text-h2 text-prism-text mb-4">Page Not Found</h2>
        <p className="text-body text-prism-text-muted mb-6">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="btn-secondary"
          >
            Go Back
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Made with Bob