import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WorkshopProvider } from './context/WorkshopContext';
import { UserProvider } from './context/UserContext';
import { WorkflowProvider } from './context/WorkflowContext';
import { WorkshopDemoLanding } from './pages/WorkshopDemoLanding';
import { TraceDataViewerDemo } from './pages/TraceDataViewerDemo';
import { ErrorBoundary, RootErrorFallback } from './components/ErrorBoundary';
import { Toaster } from 'sonner';

interface DeploymentStatus {
  lakebase_configured: boolean;
  setup_required: boolean;
  docs_url?: string;
}

/** Keep setup redirects on the browser's public origin (never an internal localhost URL). */
function sameOriginDocsUrl(docsUrl: string): string {
  const fallbackPath = '/docs/lakebase-setup/';
  try {
    const path = docsUrl.startsWith('http://') || docsUrl.startsWith('https://')
      ? new URL(docsUrl).pathname
      : docsUrl.startsWith('/')
        ? docsUrl
        : `/${docsUrl}`;
    const normalized =
      path.endsWith('/') || path.includes('.') ? path : `${path}/`;
    return `${window.location.origin}${normalized}`;
  } catch {
    return `${window.location.origin}${fallbackPath}`;
  }
}

function WorkshopAppRoutes() {
  return (
    <UserProvider>
      <WorkshopProvider>
        <WorkflowProvider>
          <Routes>
            <Route path="/" element={<WorkshopDemoLanding />} />
            <Route path="/workshop/:workshopId" element={<WorkshopDemoLanding />} />
            <Route path="/workshop/:workshopId/:phase" element={<WorkshopDemoLanding />} />
            <Route path="/trace-viewer-demo" element={<TraceDataViewerDemo />} />
          </Routes>
          <Toaster
            position="top-right"
            expand={true}
            richColors={true}
            closeButton={true}
          />
        </WorkflowProvider>
      </WorkshopProvider>
    </UserProvider>
  );
}

function DeploymentGate() {
  const [status, setStatus] = React.useState<DeploymentStatus | null>(null);
  const [statusLoaded, setStatusLoaded] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;

    async function loadDeploymentStatus() {
      try {
        const response = await fetch('/deployment/status');
        if (!response.ok) {
          throw new Error(`Deployment status failed: ${response.status}`);
        }
        const nextStatus = await response.json();
        if (!cancelled) {
          setStatus(nextStatus);
        }
      } catch {
        if (!cancelled) {
          setStatus(null);
        }
      } finally {
        if (!cancelled) {
          setStatusLoaded(true);
        }
      }
    }

    loadDeploymentStatus();

    return () => {
      cancelled = true;
    };
  }, []);

  React.useEffect(() => {
    if (status?.setup_required && !window.location.pathname.startsWith('/docs')) {
      window.location.replace(sameOriginDocsUrl(status.docs_url ?? '/docs/lakebase-setup/'));
    }
  }, [status]);

  if (!statusLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        Loading setup status...
      </div>
    );
  }

  if (status?.setup_required) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        Opening Lakebase setup docs...
      </div>
    );
  }

  return <WorkshopAppRoutes />;
}

function App() {
  return (
    <ErrorBoundary fallback={(props) => <RootErrorFallback {...props} />}>
      <Router>
        <Routes>
          <Route path="/*" element={<DeploymentGate />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
