// @spec ANNOTATION_SPEC
// @req Navigation debounced at 300ms to prevent duplicate saves
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
  { id: 'trace-3', input: 'Question 3', output: 'Answer 3', context: null },
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

describe('@spec:ANNOTATION_SPEC navigation debounce', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageStub.clear();
    vi.useFakeTimers();
    mockSubmitAnnotation.mutateAsync.mockResolvedValue({});
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('ignores a second navigation within 300ms, then allows it after the window', async () => {
    render(<AnnotationDemo />);
    expect(screen.getByText('Trace 1/3')).toBeInTheDocument();

    // Rate trace 1 and navigate: UI advances optimistically, save runs in background
    fireEvent.click(screen.getByText('4'));
    fireEvent.click(screen.getByTestId('next-trace-button'));
    expect(screen.getByText('Trace 2/3')).toBeInTheDocument();

    await advance(0);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(1);

    // A rapid second navigation inside the 300ms window is ignored:
    // no trace change and no duplicate save request.
    fireEvent.click(screen.getByRole('button', { name: /previous/i }));
    expect(screen.getByText('Trace 2/3')).toBeInTheDocument();

    await advance(0);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(1);

    // Once the 300ms window has elapsed, the same click navigates normally
    await advance(301);
    fireEvent.click(screen.getByRole('button', { name: /previous/i }));
    expect(screen.getByText('Trace 1/3')).toBeInTheDocument();

    // Navigating back without changes issues no additional save
    await advance(0);
    expect(mockSubmitAnnotation.mutateAsync).toHaveBeenCalledTimes(1);
  });
});
