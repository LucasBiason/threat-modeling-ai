import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Header, Sidebar } from './components';
import { HomePage, AnalysesListPage, AnalysisDetailPage } from './pages';
import { useState, useEffect } from 'react';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950">
      <Header
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex">
        <div className="hidden lg:block border-r border-slate-800/50">
          <Sidebar standalone />
        </div>

        <AnimatePresence>
          {sidebarOpen && (
            <>
              <button
                type="button"
                className="lg:hidden fixed inset-0 z-40 bg-black/50"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close menu"
              />
              <div className="lg:hidden fixed inset-y-0 left-0 z-50 pt-16">
                <Sidebar
                  standalone
                  onClose={() => setSidebarOpen(false)}
                  isMobile
                />
              </div>
            </>
          )}
        </AnimatePresence>

        <main className="flex-1 container mx-auto p-6 max-w-5xl">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyses" element={<AnalysesListPage />} />
            <Route path="/analyses/:id" element={<AnalysisDetailPage />} />
          </Routes>

          <footer className="mt-16 text-center text-sm text-gray-500">
            <p>Powered by multimodal LLMs com metodologia STRIDE/DREAD</p>
          </footer>
        </main>
      </div>
    </div>
  );
}

export default App;
