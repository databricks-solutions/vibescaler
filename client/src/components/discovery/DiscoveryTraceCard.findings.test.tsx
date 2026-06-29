// @spec DISCOVERY_SPEC
// @req Trace-specific analysis findings appear on the trace card, pinned above feedback (collapsible)
// AUDIT (2026-06): carries the criterion previously minted by backend data-shape tests
// (test_discovery_workspace_ui_contracts.py) — this exercises the live trace card UI.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { DiscoveryTraceCard } from './DiscoveryTraceCard';

const mockTrace = {
  id: 'trace-1',
  workshop_id: 'ws-1',
  input: '{"messages":[{"role":"user","content":"What is the capital of France?"}]}',
  output: '{"choices":[{"message":{"content":"The capital of France is Paris."}}]}',
};

const mockFeedback = [
  {
    id: 'fb-1',
    workshop_id: 'ws-1',
    trace_id: 'trace-1',
    user_id: 'user-1',
    user_name: 'Alice',
    user_email: 'alice@test.com',
    user_role: 'sme',
    feedback_label: 'good' as const,
    comment: 'Clear and accurate response',
    followup_qna: [],
    created_at: '2026-02-27T00:00:00Z',
    updated_at: '2026-02-27T00:00:00Z',
  },
];

const mockFindings = [
  {
    text: 'Brevity tolerance varies across reviewers',
    evidence_trace_ids: ['trace-1'],
    priority: 'high',
  },
];

const mockDisagreements = [
  {
    trace_id: 'trace-1',
    summary: 'Opposite ratings on accuracy vs completeness',
    underlying_theme: 'Brevity vs thoroughness',
    followup_questions: ['What level of detail is expected?'],
    facilitator_suggestions: ['Clarify completeness expectations'],
  },
];

describe('DiscoveryTraceCard analysis findings', () => {
  it('renders trace-specific findings and disagreements pinned above feedback', () => {
    render(
      <DiscoveryTraceCard
        trace={mockTrace}
        feedback={mockFeedback}
        findings={mockFindings}
        disagreements={mockDisagreements}
        onPromote={vi.fn()}
      />
    );
    const finding = screen.getByText(/Brevity tolerance varies/);
    const disagreement = screen.getByText(/Opposite ratings/);
    const feedbackComment = screen.getByText(/Clear and accurate/);
    expect(finding).toBeInTheDocument();
    expect(disagreement).toBeInTheDocument();

    // Pinned ABOVE feedback: findings precede the feedback comment in the DOM
    expect(
      finding.compareDocumentPosition(feedbackComment) & Node.DOCUMENT_POSITION_FOLLOWING
    ).toBeTruthy();
    expect(
      disagreement.compareDocumentPosition(feedbackComment) & Node.DOCUMENT_POSITION_FOLLOWING
    ).toBeTruthy();
  });

  it('findings section is collapsible', async () => {
    render(
      <DiscoveryTraceCard
        trace={mockTrace}
        feedback={mockFeedback}
        findings={mockFindings}
        disagreements={mockDisagreements}
        onPromote={vi.fn()}
      />
    );
    expect(screen.getByText(/Brevity tolerance varies/)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /AI Analysis Findings/i }));
    expect(screen.queryByText(/Brevity tolerance varies/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /AI Analysis Findings/i }));
    expect(screen.getByText(/Brevity tolerance varies/)).toBeInTheDocument();
  });

  it('does not render analysis section when no findings provided', () => {
    render(
      <DiscoveryTraceCard
        trace={mockTrace}
        feedback={mockFeedback}
        onPromote={vi.fn()}
      />
    );
    expect(screen.queryByText(/Analysis Findings/i)).not.toBeInTheDocument();
  });
});
