// @spec AUTHENTICATION_SPEC
// @req Rapid navigation: Components wait for `isLoading = false`
/**
 * Tests for UserContext authentication loading state management.
 */
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserProvider, useUser } from './UserContext';

const sessionPayload = {
  user: {
    id: 'u1',
    email: 'u1@example.com',
    name: 'U1',
    role: 'sme',
    status: 'active',
    created_at: new Date().toISOString(),
    last_active: null,
  },
  permissions: { can_annotate: true },
  provider: 'local_dev',
  provider_role: 'CAN_USE',
  project: null,
};

function LoadingStateDisplay() {
  const { isLoading } = useUser();
  return <div data-testid="loading-state">{isLoading ? 'loading' : 'ready'}</div>;
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
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => sessionPayload,
    });
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('isLoading starts true and transitions to false after session resolution', async () => {
    // Per AUTHENTICATION_SPEC: isLoading must remain true until the backend
    // session is resolved. Components should only render interactive content
    // when isLoading === false. This test verifies the transition.
    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <LoadingStateDisplay />
      </Wrapper>,
    );

    expect(screen.getByTestId('loading-state').textContent).toBe('loading');

    // After the provider-resolved session loads, isLoading becomes false
    await waitFor(() => {
      expect(screen.getByTestId('loading-state').textContent).toBe('ready');
    });

    expect(fetchMock).toHaveBeenCalledWith('/api/auth/session', expect.objectContaining({ credentials: 'include' }));
  });
});
