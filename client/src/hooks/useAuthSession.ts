import { useQuery } from '@tanstack/react-query';
import { AuthService, type AuthSession } from '@/client';

export class AuthSessionError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'AuthSessionError';
    this.status = status;
  }
}

async function fetchAuthSession(): Promise<AuthSession> {
  try {
    return await AuthService.getAuthSessionApiAuthSessionGet();
  } catch (error: unknown) {
    const apiError = error as { status?: number; body?: { detail?: string }; message?: string };
    throw new AuthSessionError(
      apiError.status ?? 0,
      apiError.body?.detail || apiError.message || 'Failed to load session',
    );
  }
}

export function useAuthSession() {
  return useQuery({
    queryKey: ['auth-session'],
    queryFn: fetchAuthSession,
    retry: false,
    staleTime: 60_000,
  });
}

