import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-prism-bg flex flex-col items-center justify-center p-8">
          <div className="card p-8 max-w-md text-center">
            <h1 className="text-4xl font-bold text-prism-red mb-4">Oops!</h1>
            <h2 className="text-2xl font-bold text-prism-text mb-4">Something went wrong</h2>
            <p className="text-prism-text-muted mb-4">
              An unexpected error occurred. Please try refreshing the page.
            </p>
            {this.state.error && (
              <details className="text-left mb-6">
                <summary className="cursor-pointer text-prism-text-muted hover:text-prism-text mb-2">
                  Error details
                </summary>
                <pre className="bg-prism-bg p-4 rounded text-xs overflow-auto max-h-40 text-prism-text-muted">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
            <button
              onClick={() => window.location.href = '/'}
              className="bg-prism-blue hover:bg-prism-blue/80 text-white font-medium px-6 py-2 rounded transition-colors"
            >
              Go Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Made with Bob