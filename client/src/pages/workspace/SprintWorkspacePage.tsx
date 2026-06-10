import React from 'react';
import { UserRole } from '@/client';
import { useUser } from '@/context/UserContext';
import { FacilitatorRootWorkspace } from '@/components/workspace/FacilitatorRootWorkspace';
import { WorkshopDemoLanding } from '@/pages/WorkshopDemoLanding';

export function SprintWorkspacePage() {
  const { user, permissions } = useUser();
  const canManageWorkspace = user?.role === UserRole.FACILITATOR || permissions?.can_manage_workshop === true;

  if (canManageWorkspace) {
    return <FacilitatorRootWorkspace />;
  }

  // SME / participant flow: discovery, annotation, and results live in the
  // phase-driven workshop experience.
  return <WorkshopDemoLanding />;
}
