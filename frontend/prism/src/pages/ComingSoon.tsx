import { TopNav } from '../components/layout/TopNav';
import { Sidebar } from '../components/layout/Sidebar';
import { Clock } from 'lucide-react';

interface ComingSoonProps {
  title: string;
}

export const ComingSoon = ({ title }: ComingSoonProps) => {
  return (
    <div className="min-h-screen bg-prism-bg flex flex-col">
      <TopNav />
      
      <div className="flex flex-1">
        <Sidebar />
        
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Clock className="w-16 h-16 text-prism-text-muted mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-prism-text mb-2">{title}</h1>
            <p className="text-prism-text-muted">This feature is coming soon</p>
          </div>
        </main>
      </div>
    </div>
  );
};

// Made with Bob
