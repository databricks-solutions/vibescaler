// @spec ROLE_PERMISSIONS_SPEC
// @req Phase advancement is gated client-side: non-facilitators are blocked from the facilitator dashboard that hosts the advance-phase control
/**
 * Asserts the CLIENT-side role gate on phase advancement. The server's
 * advance-to-* endpoints perform no role check (explicitly out of scope);
 * the only enforcement is that FacilitatorDashboard - which hosts the
 * advance-phase button - refuses to render for non-facilitators.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FacilitatorDashboard } from './FacilitatorDashboard';

// --- Mutable role state -----------------------------------------------------

const mockUserState = {
  user: { id: 'u-1', name: 'Some User', role: 'participant' } as { id: string; name: string; role: string },
};

const mockRoleCheck = {
  isFacilitator: false,
  isSME: false,
  isParticipant: true,
  canManageWorkshop: false,
  canViewAllFindings: false,
  canViewAllAnnotations: false,
  canViewResults: false,
};

vi.mock('@/hooks/useWorkshopApi', () => ({
  useWorkshop: () => ({
    data: {
      id: 'test-ws',
      current_phase: 'discovery',
      completed_phases: [],
      active_discovery_trace_ids: ['t1'],
    },
  }),
  useTraces: () => ({ data: [{ id: 't1', input: 'hi' }] }),
  useAllTraces: () => ({ data: [{ id: 't1', input: 'hi' }] }),
  useRubric: () => ({ data: null }),
  useFacilitatorAnnotations: () => ({ data: [] }),
  useFacilitatorAnnotationsWithUserDetails: () => ({ data: [] }),
  useDiscoveryFeedback: () => ({ data: [], isLoading: false }),
  useFacilitatorDiscoveryFeedback: () => ({ data: [], isLoading: false }),
  useMLflowConfig: () => ({ data: null }),
  useUpdateDiscoveryModel: () => ({ mutate: vi.fn() }),
  useDraftRubricItems: () => ({ data: [], isLoading: false }),
  useCreateDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useSuggestGroups: () => ({ mutate: vi.fn(), isPending: false }),
  useApplyGroups: () => ({ mutate: vi.fn(), isPending: false }),
  useAvailableModels: () => ({ data: undefined }),
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'test-ws' }),
}));

vi.mock('@/context/WorkflowContext', () => ({
  useWorkflowContext: () => ({ currentPhase: 'discovery', setCurrentPhase: vi.fn() }),
}));

vi.mock('@/context/UserContext', () => ({
  useUser: () => mockUserState,
  useRoleCheck: () => mockRoleCheck,
}));

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn(), refetchQueries: vi.fn() }),
}));

vi.mock('./PhaseControlButton', () => ({
  PhaseControlButton: () => <div data-testid="mock-phase-control" />,
}));

vi.mock('./SummarizationSettings', () => ({
  SummarizationSettings: () => <div data-testid="mock-summarization-settings" />,
}));

vi.mock('./DraftRubricPanel', () => ({
  DraftRubricPanel: () => <div data-testid="mock-draft-rubric-panel" />,
}));

vi.mock('./JsonPathSettings', () => ({
  JsonPathSettings: () => <div data-testid="mock-jsonpath-settings" />,
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

vi.mock('@/utils/rubricUtils', () => ({
  parseRubricQuestions: () => [],
}));

describe('@spec:ROLE_PERMISSIONS_SPEC FacilitatorDashboard role gate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 200 }),
    );
  });

  it('blocks participants: shows Facilitator Access Required and no advance-phase control', () => {
    mockUserState.user = { id: 'u-part', name: 'Part', role: 'participant' };
    mockRoleCheck.isFacilitator = false;
    mockRoleCheck.isParticipant = true;

    render(<FacilitatorDashboard onNavigate={vi.fn()} />);

    expect(screen.getByText('Facilitator Access Required')).toBeInTheDocument();
    // The advance-phase button ("Start <next phase>") must not be reachable
    expect(screen.queryByRole('button', { name: /^Start / })).not.toBeInTheDocument();
  });

  it('blocks SMEs: shows Facilitator Access Required and no advance-phase control', () => {
    mockUserState.user = { id: 'u-sme', name: 'SME', role: 'sme' };
    mockRoleCheck.isFacilitator = false;
    mockRoleCheck.isParticipant = false;
    mockRoleCheck.isSME = true;

    render(<FacilitatorDashboard onNavigate={vi.fn()} />);

    expect(screen.getByText('Facilitator Access Required')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^Start / })).not.toBeInTheDocument();
  });

  it('renders the advance-phase control for facilitators (gate is role-based)', () => {
    mockUserState.user = { id: 'u-fac', name: 'Fac', role: 'facilitator' };
    mockRoleCheck.isFacilitator = true;
    mockRoleCheck.isSME = false;
    mockRoleCheck.isParticipant = false;
    mockRoleCheck.canManageWorkshop = true;
    mockRoleCheck.canViewAllFindings = true;
    mockRoleCheck.canViewAllAnnotations = true;
    mockRoleCheck.canViewResults = true;

    render(<FacilitatorDashboard onNavigate={vi.fn()} />);

    expect(screen.queryByText('Facilitator Access Required')).not.toBeInTheDocument();
    // currentPhase=discovery -> next phase is rubric -> "Start Rubric Creation"
    expect(screen.getByRole('button', { name: /Start Rubric Creation/ })).toBeInTheDocument();
  });
});
