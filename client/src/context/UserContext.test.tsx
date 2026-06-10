// @spec AUTHENTICATION_SPEC
// @req Rapid navigation: Components wait for `isLoading = false`
/**
 * Tests for UserContext authentication loading state management.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserProvider, useUser } from './UserContext';

// Node 26 ships an experimental global localStorage that is undefined unless
// --localstorage-file is provided, shadowing jsdom's implementation. Stub an
// in-memory shim so UserContext's localStorage access works in tests.
const localStorageStub = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => (key in store ? store[key] : null),
    setItem: (key: string, value: string) => {
      store[key] = String(value);
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();
vi.stubGlobal('localStorage', localStorageStub);

// Mock the UsersService
vi.mock('@/client', () => ({
  UsersService: {
    getUserUsersUserIdGet: vi.fn(),
    getUserPermissionsUsersUserIdPermissionsGet: vi.fn(),
    updateLastActiveUsersUsersUserIdLastActivePut: vi.fn(),
  },
}));

import { UsersService } from '@/client';

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

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
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
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

  it('isLoading stays true until user validation AND permission loading complete', async () => {
    // Per AUTHENTICATION_SPEC: isLoading must remain true until ALL
    // initialization steps complete, including permission loading. Rapidly
    // navigating components observe isLoading === true the whole time the
    // saved session is being validated.
    const savedUser = { id: 'u1', name: 'Saved User', role: 'participant', created_at: '2026-01-01' };
    localStorage.setItem('workshop_user', JSON.stringify(savedUser));

    const userRequest = deferred<typeof savedUser>();
    const permissionsRequest = deferred<Record<string, boolean>>();
    vi.mocked(UsersService.getUserUsersUserIdGet).mockReturnValue(userRequest.promise as never);
    vi.mocked(UsersService.getUserPermissionsUsersUserIdPermissionsGet).mockReturnValue(
      permissionsRequest.promise as never,
    );

    const Wrapper = createWrapper();
    render(
      <Wrapper>
        <LoadingStateDisplay />
      </Wrapper>,
    );

    // User validation request still in flight: components must see loading
    expect(screen.getByTestId('loading-state').textContent).toBe('loading');

    // Resolve user validation; permissions are still in flight, so isLoading
    // must STILL be true (the race condition this spec guards against)
    await act(async () => {
      userRequest.resolve(savedUser);
    });
    expect(screen.getByTestId('loading-state').textContent).toBe('loading');

    // Only after permissions resolve does isLoading become false
    await act(async () => {
      permissionsRequest.resolve({ can_annotate: true, can_view_rubric: true });
    });
    await waitFor(() => {
      expect(screen.getByTestId('loading-state').textContent).toBe('ready');
    });
  });
});
