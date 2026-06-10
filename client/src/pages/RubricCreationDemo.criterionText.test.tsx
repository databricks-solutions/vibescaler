// @spec RUBRIC_SPEC
// @req Questions with multi-line descriptions parse correctly
import { describe, expect, it, vi, beforeAll, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RubricCreationDemo } from './RubricCreationDemo';

// jsdom in this setup does not provide localStorage (used for the scratch pad)
beforeAll(() => {
  if (!globalThis.localStorage) {
    const store = new Map<string, string>();
    Object.defineProperty(globalThis, 'localStorage', {
      value: {
        getItem: (key: string) => store.get(key) ?? null,
        setItem: (key: string, value: string) => { store.set(key, String(value)); },
        removeItem: (key: string) => { store.delete(key); },
        clear: () => store.clear(),
      },
      writable: true,
    });
  }
});

// --- mock return values ---------------------------------------------------

const mockRubric = {
  data: null as Record<string, unknown> | null,
  isLoading: false,
  error: null,
};
const emptyFeedback = { data: [], refetch: vi.fn(), isRefetching: false };

vi.mock('@/hooks/useWorkshopApi', () => ({
  useRubric: () => mockRubric,
  useCreateRubric: () => ({ mutateAsync: vi.fn() }),
  useUpdateRubric: () => ({ mutateAsync: vi.fn() }),
  useDiscoveryFeedback: () => emptyFeedback,
  useFacilitatorDiscoveryFeedback: () => emptyFeedback,
  useAllTraces: () => ({ data: [], refetch: vi.fn() }),
  useAllParticipantNotes: () => ({ data: [] }),
  useWorkshopAnnotationConfig: () => ({ data: { show_participant_notes: false } }),
  useToggleParticipantNotes: () => ({ mutate: vi.fn(), isPending: false }),
  useAvailableModels: () => ({ data: [] }),
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'ws-1' }),
}));

vi.mock('@/context/WorkflowContext', () => ({
  useWorkflowContext: () => ({ setCurrentPhase: vi.fn() }),
}));

vi.mock('@/context/UserContext', () => ({
  useUser: () => ({ user: { id: 'u1', name: 'Facilitator' } }),
  useRoleCheck: () => ({ isFacilitator: true }),
}));

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ setQueryData: vi.fn(), invalidateQueries: vi.fn() }),
}));

vi.mock('@/components/FocusedAnalysisView', () => ({
  FocusedAnalysisView: () => null,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

const openRubricTab = () => {
  render(<RubricCreationDemo />);
  fireEvent.mouseDown(screen.getByRole('tab', { name: /Rubric Questions/i }));
};

describe('@spec:RUBRIC_SPEC RubricCreationDemo criterion text', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockRubric.data = null;
  });

  it('renders multi-line binary criterion custom text fully, without truncation', () => {
    mockRubric.data = {
      id: 'r1',
      question:
        'Safety: Binary check\nPositive: Pass line 1\nPass line 2\nNegative: Fail line 1\nFail line 2|||JUDGE_TYPE|||binary',
      judge_type: 'binary',
      binary_labels: { pass: 'Pass', fail: 'Fail' },
    };

    openRubricTab();

    const positive = screen.getByText(/Pass line 1/);
    expect(positive.textContent).toBe('Pass line 1\nPass line 2');
    expect(positive).toHaveClass('whitespace-pre-wrap');

    const negative = screen.getByText(/Fail line 1/);
    expect(negative.textContent).toBe('Fail line 1\nFail line 2');
    expect(negative).toHaveClass('whitespace-pre-wrap');
  });

  it('does not offer Free-form as an evaluation type in the criterion dialog', () => {
    openRubricTab();

    fireEvent.click(screen.getByRole('button', { name: /Create First Criterion/i }));

    expect(screen.getAllByText('Likert Scale').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Binary').length).toBeGreaterThan(0);
    expect(screen.queryByText('Free-form')).not.toBeInTheDocument();
  });

  it('renders legacy freeform criteria as likert without crashing', () => {
    mockRubric.data = {
      id: 'r1',
      question: 'Feedback: Provide detailed feedback|||JUDGE_TYPE|||freeform',
      judge_type: 'likert',
      binary_labels: null,
    };

    openRubricTab();

    expect(screen.getByText('Feedback')).toBeInTheDocument();
    expect(screen.getAllByText('Likert Scale').length).toBeGreaterThan(0);
    expect(screen.queryByText('Free-form')).not.toBeInTheDocument();
  });
});
