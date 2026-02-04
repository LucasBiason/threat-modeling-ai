import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ShieldAlert, Menu } from 'lucide-react';
import { UploadSection, ResultsSection, ErrorMessage, Sidebar } from './components';
import { useThreatAnalysis } from './hooks/useThreatAnalysis';

function App() {
  const {
    file,
    analysis,
    loading,
    error,
    confidence,
    iou,
    sidebarOpen,
    setFile,
    runAnalysis,
    setConfidence,
    setIou,
    setSidebarOpen,
  } = useThreatAnalysis();

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setSidebarOpen]);

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-7xl">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-gray-400 hover:text-white"
              aria-label="Menu"
            >
              <Menu className="w-6 h-6" />
            </button>
            <ShieldAlert className="text-indigo-500 w-10 h-10" />
            <div>
              <h1 className="text-xl font-bold tracking-tight">CloudSec AI</h1>
              <p className="text-gray-400 text-xs">STRIDE/DREAD para diagramas de arquitetura</p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar - Desktop */}
        <div className="hidden lg:block border-r border-slate-800/50">
          <Sidebar
            confidence={confidence}
            iou={iou}
            onConfidenceChange={setConfidence}
            onIouChange={setIou}
          />
        </div>

        {/* Drawer overlay - Mobile */}
        <AnimatePresence>
          {sidebarOpen && (
            <>
              <button
                type="button"
                className="lg:hidden fixed inset-0 z-40 bg-black/50"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close menu"
              />
              <div className="lg:hidden fixed inset-y-0 left-0 z-50">
                <Sidebar
                  confidence={confidence}
                  iou={iou}
                  onConfidenceChange={setConfidence}
                  onIouChange={setIou}
                  onClose={() => setSidebarOpen(false)}
                  isMobile
                />
              </div>
            </>
          )}
        </AnimatePresence>

        <main className="flex-1 container mx-auto p-6 max-w-5xl">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            <div className="space-y-6">
              <UploadSection
                file={file}
                loading={loading}
                onFileSelect={setFile}
                onAnalyze={runAnalysis}
              />
              {error && (
                <ErrorMessage message={error} onDismiss={() => setFile(null)} />
              )}
            </div>
            <AnimatePresence>
              {analysis && <ResultsSection analysis={analysis} />}
            </AnimatePresence>
          </div>

          <footer className="mt-16 text-center text-sm text-gray-500">
            <p>Powered by multimodal LLMs com metodologia STRIDE/DREAD</p>
          </footer>
        </main>
      </div>
    </div>
  );
}

export default App;
