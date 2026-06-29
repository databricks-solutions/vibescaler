import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { UserRole } from '@/client';
import { IntakePage } from '@/pages/IntakePage';
import { FacilitatorDashboard } from '@/components/FacilitatorDashboard';
import { FacilitatorUserManager } from '@/components/FacilitatorUserManager';
import { useUser } from '@/context/UserContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { isProjectSetupApiError, isSetupBlockingStatus, useProjectSetupStatus } from '@/hooks/useProjectSetupApi';
import { SetupProgressCard } from './SetupProgressCard';

export function FacilitatorRootWorkspace() {
  const navigate = useNavigate();
  const { user, permissions } = useUser();
  const setupStatus = useProjectSetupStatus({ enabled: !!user });
  const canManageSetup = user?.role === UserRole.FACILITATOR || permissions?.can_manage_workshop === true;

  if (!canManageSetup) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader>
            <CardTitle>Facilitator access required</CardTitle>
            <CardDescription>
              This workspace is available for facilitator accounts.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (setupStatus.isLoading) {
    return (
      <div className="flex min-h-96 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (setupStatus.data && isSetupBlockingStatus(setupStatus.data.status)) {
    return (
      <div className="p-6">
        <SetupProgressCard
          progress={setupStatus.data}
          onRetry={() => navigate('/project/setup')}
        />
      </div>
    );
  }

  if (setupStatus.error && !isProjectSetupApiError(setupStatus.error)) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader>
            <CardTitle>Setup status unavailable</CardTitle>
            <CardDescription>
              We could not load setup status. Refresh the page to try again.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  const handleDashboardNavigate = () => {
    // The root workspace keeps controls on one page.
  };

  return (
    <div className="space-y-8 p-6">
      <section>
        <Card className="border-indigo-200 bg-indigo-50/30">
          <CardHeader>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant="secondary">Workspace Activity Monitor</Badge>
                  <Badge variant="outline">Sprint #1 · proposed</Badge>
                </div>
                <CardTitle>Establish baseline rubric</CardTitle>
                <CardDescription className="mt-2 max-w-2xl">
                  The first active Sprint is goal context for Review Feed, Grading, and confidence-building work.
                  It is not a phase or project lifecycle state.
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => navigate('/project/setup')}>
                Edit Project Settings
              </Button>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 lg:grid-cols-3">
            <StarterArtifactCard
              eyebrow="Grading"
              title="Starter Rubric"
              description="Draft Criteria seeded from the System Under Review context."
            >
              <Badge variant="destructive">Rubric review required</Badge>
              <p className="text-xs text-muted-foreground">
                #132 must be satisfied before Rubric-dependent Review Feed work is SME-ready.
              </p>
            </StarterArtifactCard>
            <StarterArtifactCard
              eyebrow="Review Feed"
              title="Starter Review Feed"
              description="A proposed working set the Developer can inspect before SME Reviewers begin."
            >
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <span className="rounded-md border bg-background p-2">6 diverse</span>
                <span className="rounded-md border bg-background p-2">4 edge</span>
                <span className="rounded-md border bg-background p-2">2 audit</span>
              </div>
            </StarterArtifactCard>
            <StarterArtifactCard
              eyebrow="Evaluation Goals"
              title="Default Sprint Goals"
              description="Defaults keep the Sprint editable while giving the Developer an immediate starting point."
            >
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">human agreement</Badge>
                <Badge variant="outline">judge-human agreement</Badge>
                <Badge variant="outline">confidence</Badge>
              </div>
            </StarterArtifactCard>
          </CardContent>
        </Card>
      </section>

      <section>
        <Card>
          <CardContent className="pt-6">
            <IntakePage />
          </CardContent>
        </Card>
      </section>

      <section>
        <Card>
          <CardHeader>
            <CardTitle>Invite Participants</CardTitle>
            <CardDescription>
              Add workshop users and update SME or participant roles.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FacilitatorUserManager />
          </CardContent>
        </Card>
      </section>

      <section>
        <Card>
          <CardHeader>
            <CardTitle>Facilitator Dashboard</CardTitle>
            <CardDescription>
              Monitor current workshop activity and operational metrics.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FacilitatorDashboard onNavigate={handleDashboardNavigate} />
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

function StarterArtifactCard({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="bg-background">
      <CardHeader>
        <div className="text-[10px] uppercase tracking-[0.12em] text-muted-foreground">{eyebrow}</div>
        <CardTitle className="text-base">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">{children}</CardContent>
    </Card>
  );
}
