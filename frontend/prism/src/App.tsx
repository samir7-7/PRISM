import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { CLISplash } from './pages/CLISplash';
import { Dashboard } from './pages/Dashboard';
import { Tests } from './pages/Tests';
import { ComingSoon } from './pages/ComingSoon';
import { Report } from './pages/Report';
import { NotFound } from './pages/NotFound';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CLISplash />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/tests" element={<Tests />} />
          <Route
            path="/dashboard/timeline"
            element={<ComingSoon title="Timeline View" />}
          />
          <Route
            path="/dashboard/impact"
            element={<ComingSoon title="Impact Analysis" />}
          />
          <Route path="/report/:id" element={<Report />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;

// Made with Bob
