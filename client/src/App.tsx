import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { WorkshopProvider } from './context/WorkshopContext';
import { UserProvider } from './context/UserContext';
import { WorkflowProvider } from './context/WorkflowContext';
import { TraceDataViewerDemo } from './pages/TraceDataViewerDemo';
import { ProjectSetupGate } from './pages/ProjectSetupGate';
import { ProjectSetupPage } from './pages/ProjectSetupPage';
import { UserShell } from './pages/shell/UserShell';
import { WorkshopShell } from './pages/shell/WorkshopShell';
import { WorkflowShell } from './pages/shell/WorkflowShell';
import { SprintWorkspacePage } from './pages/workspace/SprintWorkspacePage';
import { ErrorBoundary, RootErrorFallback } from './components/ErrorBoundary';
import { useWorkshopContext } from './context/WorkshopContext';
import { useUser } from './context/UserContext';
import { useWorkshopMeta } from './hooks/useWorkshopApi';
import { ChevronRight } from 'lucide-react';
import { Toaster } from 'sonner';

export function AppShellPathBar() {
  const { user, permissions } = useUser();
  const { workshopId, setWorkshopId } = useWorkshopContext();
  const { data: workshopMeta } = useWorkshopMeta(workshopId || '');
  const location = useLocation();
  const navigate = useNavigate();

  if (!user || location.pathname === '/trace-viewer-demo') {
    return null;
  }

  const canManageSetup = permissions?.can_manage_workshop === true;
  const isProjectSetup = location.pathname === '/project/setup';
  const hasWorkshop = !!workshopId && !workshopId.startsWith('temp-');
  const workshopLabel = hasWorkshop ? (workshopMeta?.name || 'Workshop') : 'Workshop selection';

  const handleProjectSetupClick = () => {
    if (isProjectSetup) return;
    navigate('/project/setup');
  };

  const handleWorkshopClick = () => {
    if (!hasWorkshop) return;
    setWorkshopId(null);
    navigate('/');
  };

  return (
    <div className="border-b px-6 py-3 bg-background">
      <nav aria-label="App shell path" className="text-xs text-muted-foreground flex items-center gap-2">
        <span className="font-semibold text-foreground">
          Me ({user.name || user.email || 'User'})
        </span>
        {canManageSetup && (
          <>
            <ChevronRight className="h-3 w-3" />
            {isProjectSetup ? (
              <span className="font-semibold text-foreground">Project setup</span>
            ) : (
              <button
                type="button"
                className="font-semibold text-foreground hover:underline"
                onClick={handleProjectSetupClick}
              >
                Project setup
              </button>
            )}
          </>
        )}
        {!isProjectSetup && <ChevronRight className="h-3 w-3" />}
        {hasWorkshop ? (
          <button
            type="button"
            className="font-semibold text-foreground hover:underline"
            onClick={handleWorkshopClick}
          >
            {workshopLabel}
          </button>
        ) : (
          <span className="font-semibold text-foreground">{workshopLabel}</span>
        )}
      </nav>
    </div>
  );
}

function AppRoutes() {
  return (
    <>
      <AppShellPathBar />
      <Routes>
        <Route element={<UserShell />}>
          <Route path="/project/setup" element={<ProjectSetupPage />} />
          <Route element={<ProjectSetupGate />}>
            <Route index element={<SprintWorkspacePage />} />
          </Route>
          <Route element={<WorkshopShell />}>
            <Route element={<WorkflowShell />}>
              <Route path="/workshop/:workshopId" element={<SprintWorkspacePage />} />
              <Route path="/workshop/:workshopId/:phase" element={<SprintWorkspacePage />} />
            </Route>
          </Route>
        </Route>
        <Route path="/trace-viewer-demo" element={<TraceDataViewerDemo />} />
      </Routes>
    </>
  );
}

interface DeploymentStatus {
  lakebase_configured: boolean;
  setup_required: boolean;
  docs_url?: string;
}

/** Keep setup redirects on the browser's public origin (never an internal localhost URL). */
export function sameOriginDocsUrl(docsUrl: string): string {
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

function GatedAppShell() {
  return (
    <UserProvider>
      <WorkshopProvider>
        <WorkflowProvider>
          <AppRoutes />
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

  return <GatedAppShell />;
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
