// @spec DISCOVERY_SPEC
// @req Analysis shows warning (not error) if < 2 participants
// Regression guard: the old DiscoveryAnalysisTab rendered a "Limited Participant
// Data" warning (default Alert variant, never destructive) when an analysis was
// based on fewer than 2 participants. The live FacilitatorDiscoveryWorkspace
// must keep that behavior.
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FacilitatorDiscoveryWorkspace } from './FacilitatorDiscoveryWorkspace';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { DiscoveryAnalysis } from '@/hooks/useWorkshopApi';

const mockAnalyses: { data: DiscoveryAnalysis[] | undefined } = { data: undefined };

vi.mock('@/hooks/useWorkshopApi', () => ({
  useAllTraces: () => ({ data: [
    { id: 't1', workshop_id: 'ws-1', input: 'User question 1', output: 'Answer 1' },
  ] }),
  useFacilitatorDiscoveryFeedback: () => ({ data: [] }),
  useDiscoveryAnalyses: () => mockAnalyses,
  useRunDiscoveryAnalysis: () => ({ mutate: vi.fn(), isPending: false }),
  useDraftRubricItems: () => ({ data: [] }),
  useCreateDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteDraftRubricItem: () => ({ mutate: vi.fn(), isPending: false }),
  useSuggestGroups: () => ({ mutate: vi.fn(), isPending: false }),
  useApplyGroups: () => ({ mutate: vi.fn(), isPending: false }),
  useCreateRubricFromDraft: () => ({ mutate: vi.fn(), isPending: false }),
  useWorkshop: () => ({ data: { id: 'ws-1', current_phase: 'discovery', discovery_started: true, active_discovery_trace_ids: ['t1'] } }),
  useWorkshopDiscoveryConfig: () => ({ data: { discovery_questions_model_name: null, discovery_randomize_traces: false, active_discovery_trace_ids: ['t1'] } }),
  useWorkshopPhase: () => ({ data: { current_phase: 'discovery', completed_phases: [], discovery_started: true, annotation_started: false } }),
  useMLflowConfig: () => ({ data: null }),
  useUpdateDiscoveryModel: () => ({ mutate: vi.fn() }),
  useUpdateDiscoverySettings: () => ({ mutate: vi.fn(), isPending: false }),
  useAvailableModels: () => ({ data: undefined }),
  useDiscoveryComments: () => ({ data: [], refetch: vi.fn() }),
  useCreateDiscoveryComment: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useVoteDiscoveryComment: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteDiscoveryComment: () => ({ mutate: vi.fn(), isPending: false }),
  useDiscoveryAgentRun: () => ({ data: undefined }),
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'ws-1' }),
}));

vi.mock('@/context/UserContext', () => ({
  useUser: () => ({ user: { id: 'facilitator-1', role: 'facilitator' } }),
  useRoleCheck: () => ({ isFacilitator: true }),
}));

vi.mock('sonner', () => ({ toast: Object.assign(vi.fn(), { success: vi.fn(), error: vi.fn() }) }));

function makeAnalysis(overrides: Partial<DiscoveryAnalysis> = {}): DiscoveryAnalysis {
  return {
    id: 'analysis-1', workshop_id: 'ws-1', template_used: 'evaluation_criteria',
    analysis_data: 'Summary.', findings: [],
    disagreements: { high: [], medium: [], lower: [] },
    participant_count: 5, model_used: 'test-model',
    created_at: '2026-06-09T10:30:00Z', updated_at: '2026-06-09T10:30:00Z',
    ...overrides,
  };
}

function renderWorkspace() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <FacilitatorDiscoveryWorkspace onNavigate={vi.fn()} />
    </QueryClientProvider>
  );
}

describe('FacilitatorDiscoveryWorkspace - <2 participant warning', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAnalyses.data = undefined;
  });

  it('shows warning alert when participant_count is 1', () => {
    mockAnalyses.data = [makeAnalysis({ participant_count: 1 })];
    renderWorkspace();
    expect(screen.getByText('Limited Participant Data')).toBeInTheDocument();
    expect(screen.getByText(/based on feedback from only 1 participant\./)).toBeInTheDocument();
  });

  it('shows warning alert when participant_count is 0', () => {
    mockAnalyses.data = [makeAnalysis({ participant_count: 0 })];
    renderWorkspace();
    expect(screen.getByText('Limited Participant Data')).toBeInTheDocument();
    expect(screen.getByText(/based on feedback from only 0 participants\./)).toBeInTheDocument();
  });

  it('does NOT show warning when participant_count >= 2', () => {
    mockAnalyses.data = [makeAnalysis({ participant_count: 2 })];
    renderWorkspace();
    expect(screen.queryByText('Limited Participant Data')).not.toBeInTheDocument();
  });

  it('warning is a warning, not an error (default Alert variant, not destructive)', () => {
    mockAnalyses.data = [makeAnalysis({ participant_count: 1 })];
    const { container } = renderWorkspace();
    const alertEl = container.querySelector('[role="alert"]');
    expect(alertEl).toBeInTheDocument();
    expect(alertEl!.textContent).toContain('Limited Participant Data');
    expect(alertEl!.className).not.toContain('destructive');
  });
});
