// @spec ANNOTATION_SPEC
// @req Completing the final trace shows a terminal completion state
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { act, render, screen, fireEvent, waitFor } from '@testing-library/react';
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

const NAVIGATION_DEBOUNCE_WAIT_MS = 350;

const waitForDebounce = () =>
  act(() => new Promise<void>((resolve) => setTimeout(resolve, NAVIGATION_DEBOUNCE_WAIT_MS)));

const annotateAllTraces = async () => {
  // Trace 1: rate and go next
  fireEvent.click(screen.getByText('4'));
  fireEvent.click(screen.getByTestId('next-trace-button'));

  // Trace 2 (last): rate and complete
  await screen.findByTestId('complete-annotation-button');
  await waitForDebounce();
  fireEvent.click(screen.getByText('4'));
  fireEvent.click(screen.getByTestId('complete-annotation-button'));
};

describe('@spec:ANNOTATION_SPEC annotation completion terminal state', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageStub.clear();
    mockSubmitAnnotation.mutateAsync.mockResolvedValue({});
  });

  it('replaces the trace UI with a terminal completion screen after completing the last trace', async () => {
    render(<AnnotationDemo />);

    expect(screen.getByText('Rate this Response')).toBeInTheDocument();

    await annotateAllTraces();

    await screen.findByTestId('annotation-complete-screen');
    expect(screen.getByText('All Annotations Complete!')).toBeInTheDocument();

    // The trace UI (and its Complete button) is gone, so completion cannot re-trigger
    expect(screen.queryByText('Rate this Response')).not.toBeInTheDocument();
    expect(screen.queryByTestId('complete-annotation-button')).not.toBeInTheDocument();
    expect(mockToast.success).not.toHaveBeenCalled();
  });

  it('allows returning to the annotation view to review, then completes back to the terminal state', async () => {
    render(<AnnotationDemo />);

    await annotateAllTraces();
    await screen.findByTestId('annotation-complete-screen');

    fireEvent.click(screen.getByTestId('review-annotations-button'));

    // Back on the last trace with the rating UI available for edits
    expect(screen.getByText('Rate this Response')).toBeInTheDocument();
    expect(screen.queryByTestId('annotation-complete-screen')).not.toBeInTheDocument();

    // Completing again (no changes) returns to the terminal state without an error
    await waitForDebounce();
    fireEvent.click(screen.getByTestId('complete-annotation-button'));

    await screen.findByTestId('annotation-complete-screen');
    await waitFor(() => {
      expect(mockToast.error).not.toHaveBeenCalled();
    });
  });
});
