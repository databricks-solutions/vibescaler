// @spec DISCOVERY_SPEC
// @req Data freshness banner (participant count, last run timestamp)
// AUDIT (2026-06): carries the criterion previously minted by tests of the unmounted
// DiscoveryAnalysisTab — the live workspace shows analysis freshness metadata
// (participant count, run timestamp, template) in the CrossTraceAnalysisSummary header.
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CrossTraceAnalysisSummary } from './CrossTraceAnalysisSummary';

const mockAnalysis = {
  id: 'analysis-1',
  workshop_id: 'ws-1',
  template_used: 'evaluation_criteria',
  analysis_data: 'Reviewers consistently disagree about brevity vs completeness.',
  findings: [
    { text: 'Brevity tolerance varies', evidence_trace_ids: ['t1', 't2'], priority: 'high' },
  ],
  disagreements: { high: [], medium: [], lower: [] },
  participant_count: 4,
  model_used: 'claude-sonnet-4.5',
  created_at: '2026-02-27T00:00:00Z',
  updated_at: '2026-02-27T00:00:00Z',
};

describe('CrossTraceAnalysisSummary freshness metadata', () => {
  it('displays the participant count for the analysis run', () => {
    render(<CrossTraceAnalysisSummary analysis={mockAnalysis} onPromote={vi.fn()} />);
    expect(screen.getByText(/4 participants/)).toBeInTheDocument();
  });

  it('displays the last run timestamp', () => {
    render(<CrossTraceAnalysisSummary analysis={mockAnalysis} onPromote={vi.fn()} />);
    const expected = new Date(mockAnalysis.created_at).toLocaleString();
    expect(screen.getByText(expected)).toBeInTheDocument();
  });

  it('displays which template produced the analysis', () => {
    render(<CrossTraceAnalysisSummary analysis={mockAnalysis} onPromote={vi.fn()} />);
    expect(screen.getByText(/Eval Criteria/)).toBeInTheDocument();
  });
});
