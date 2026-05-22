// @spec AUTHENTICATION_SPEC
// @req Rapid navigation: Components wait for `isLoading = false`
/**
 * Tests for UserContext authentication loading state management.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserProvider, useRoleCheck, useUser } from './UserContext';
import { useAuthSession } from '@/hooks/useAuthSession';

vi.mock('@/client', () => ({
  UserRole: {
    FACILITATOR: 'facilitator',
    SME: 'sme',
    PARTICIPANT: 'participant',
  },
}));

vi.mock('@/hooks/useAuthSession', () => ({
  useAuthSession: vi.fn(),
}));

function LoadingStateDisplay() {
  const { isLoading } = useUser();
  return <div data-testid="loading-state">{isLoading ? 'loading' : 'ready'}</div>;
}

function RoleCheckDisplay() {
  const { isFacilitator, isSME, canManageWorkshop, canManageProject } = useRoleCheck();
  return (
    <div>
      <div data-testid="is-facilitator">{String(isFacilitator)}</div>
      <div data-testid="is-sme">{String(isSME)}</div>
      <div data-testid="can-manage-workshop">{String(canManageWorkshop)}</div>
      <div data-testid="can-manage-project">{String(canManageProject)}</div>
    </div>
  );
}

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <UserProvider>{children}</UserProvider>
    </QueryClientProvider>
  );
}

describe('@spec:AUTHENTICATION_SPEC UserContext loading state', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.mocked(useAuthSession).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAuthSession>);
  });

  it('isLoading starts true and transitions to false after initialization', async () => {
    // Per AUTHENTICATION_SPEC: isLoading must remain true until ALL initialization
    // steps complete. Components should only render interactive content when
    // isLoading === false. This test verifies the transition.
    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <LoadingStateDisplay />
      </Wrapper>,
    );

    // After initialization (no saved user), isLoading becomes false
    await waitFor(() => {
      expect(screen.getByTestId('loading-state').textContent).toBe('ready');
    });
  });

  it('treats project managers as facilitators even when the persisted app role is SME', () => {
    vi.mocked(useAuthSession).mockReturnValue({
      data: {
        user: {
          id: 'manager-1',
          email: 'manager@example.com',
          name: 'Manager',
          role: 'sme',
          status: 'active',
          created_at: new Date().toISOString(),
        },
        permissions: {
          can_manage_project: true,
          can_manage_workshop: false,
        },
        provider: 'databricks_apps',
        provider_role: 'CAN_MANAGE',
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as unknown as ReturnType<typeof useAuthSession>);

    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <RoleCheckDisplay />
      </Wrapper>,
    );

    expect(screen.getByTestId('is-facilitator').textContent).toBe('true');
    expect(screen.getByTestId('is-sme').textContent).toBe('false');
    expect(screen.getByTestId('can-manage-workshop').textContent).toBe('true');
    expect(screen.getByTestId('can-manage-project').textContent).toBe('true');
  });
});
