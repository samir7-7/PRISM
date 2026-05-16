import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CLISplash } from './pages/CLISplash';
import { Dashboard } from './pages/Dashboard';
import { Tests } from './pages/Tests';
import { ComingSoon } from './pages/ComingSoon';
import { Report } from './pages/Report';

function App() {
  return (
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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

// Made with Bob
