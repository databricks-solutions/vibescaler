// @spec ANNOTATION_SPEC
// @req Failed saves are queued and retried automatically with exponential backoff
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { act, render, screen, fireEvent } from '@testing-library/react';
import { AnnotationDemo } from './AnnotationDemo';

const mockSubmitAnnotation = { mutateAsync: vi.fn() };
const mockToast = { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() };

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

vi.mock('@/components/TraceViewer', () => ({
  TraceViewer: () => <div data-testid="trace-viewer-stub" />,
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'ws-1' }),
}));

vi.mock('@/context/UserContext', () => ({
  useUser: () => ({ user: { id: 'sme-1', name: 'SME One', role: 'sme' } }),
  useRoleCheck: () => ({ canAnnotate: true }),
}));

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({}),
}));

vi.mock('sonner', () => ({
  toast: {
    success: (...args: unknown[]) => mockToast.success(...args),
    error: (...args: unknown[]) => mockToast.error(...args),
    warning: (...args: unknown[]) => mockToast.warning(...args),
    info: (...args: unknown[]) => mockToast.info(...args),
  },
}));

const traces = [
  { id: 'trace-1', input: 'Question 1', output: 'Answer 1', context: null },
  { id: 'trace-2', input: 'Question 2', output: 'Answer 2', context: null },
];

const rubric = {
  id: 'rubric-1',
  question: 'Accuracy: Is the response accurate?|||JUDGE_TYPE|||likert',
};

vi.mock('@/hooks/useWorkshopApi', () => ({
  useTraces: () => ({ data: traces, isLoading: false, error: null }),
  useRubric: () => ({ data: rubric, isLoading: false }),
  useUserAnnotations: () => ({ data: [] }),
  useMLflowConfig: () => ({ data: null }),
  useSubmitAnnotation: () => mockSubmitAnnotation,
  refetchAllWorkshopQueries: vi.fn(),
  useWorkshopAnnotationConfig: () => ({ data: { show_participant_notes: false } }),
  useParticipantNotes: () => ({ data: [] }),
  useSubmitParticipantNote: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useDeleteParticipantNote: () => ({ mutateAsync: vi.fn() }),
}));

const advance = (ms: number) =>
  act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });

/** Rate the current trace and navigate, which kicks off a background save. */
const rateAndGoNext = () => {
  fireEvent.click(screen.getByText('4'));
  fireEvent.click(screen.getByTestId('next-trace-button'));
};

describe('@spec:ANNOTATION_SPEC background save retry with exponential backoff', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageStub.clear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('retries a failed background save at 1s/2s/4s, then queues it and warns once', async () => {
    mockSubmitAnnotation.mutateAsync.mockRejectedValue(new Error('network down'));
    render(<AnnotationDemo />);

    rateAndGoNext();

    // Attempt 1 fires immediately with the background save
    await advance(0);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(1);

    // Retry 1 after 1s (not before)
    await advance(999);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(1);
    await advance(1);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(2);

    // Retry 2 after 2s more (not before)
    await advance(1999);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(2);
    await advance(1);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(3);

    // Retry 3 after 4s more (not before) — max attempts = 1 initial + 3 retries
    await advance(3999);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(3);
    await advance(1);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(4);

    // Backoff exhausted: annotation is queued for recovery and the user is
    // warned once. Navigation already happened optimistically (no error UI).
    await advance(0);
    expect(mockToast.warning).toHaveBeenCalledTimes(1);
    expect(mockToast.warning).toHaveBeenCalledWith('Retrying save', expect.anything());
    expect(screen.getByText('Retry 1')).toBeInTheDocument();
    expect(mockToast.success).not.toHaveBeenCalled();
  });

  it('automatically drains the failed-save queue once saves succeed again', async () => {
    mockSubmitAnnotation.mutateAsync.mockRejectedValue(new Error('network down'));
    render(<AnnotationDemo />);

    rateAndGoNext();

    // Exhaust the backoff window (0s + 1s + 2s + 4s = 4 attempts by t=7s)
    await advance(7000);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(4);
    expect(screen.getByText('Retry 1')).toBeInTheDocument();

    // Network restored: the periodic queue processor (5s cadence, with a 5s
    // minimum gap since the last attempt) retries and succeeds at t=15s.
    mockSubmitAnnotation.mutateAsync.mockResolvedValue({});
    await advance(8000);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(5);
    expect(screen.queryByText('Retry 1')).not.toBeInTheDocument();

    // Automatic recovery is silent — success toasts are reserved for manual bulk retry
    expect(mockToast.success).not.toHaveBeenCalled();
  });
});
