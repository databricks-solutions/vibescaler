// @spec DISCOVERY_SPEC
// @req Facilitator selects analysis template (Evaluation Criteria or Themes & Patterns) before running
// AUDIT (2026-06): carries the criterion previously minted by tests of the unmounted
// DiscoveryAnalysisTab — this exercises the live overview bar's template selector.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { DiscoveryOverviewBar } from './DiscoveryOverviewBar';

const defaultProps = {
  participantCount: 4,
  traceCount: 10,
  feedbackCount: 28,
  currentModel: 'Claude Sonnet 4.5',
  modelOptions: [
    { value: 'Claude Sonnet 4.5', label: 'Claude Sonnet 4.5', disabled: false },
  ],
  onRunAnalysis: vi.fn(),
  onModelChange: vi.fn(),
  onPauseToggle: vi.fn(),
  onAddTraces: vi.fn(),
  isPaused: false,
  isAnalysisRunning: false,
  hasMlflowConfig: true,
};

describe('DiscoveryOverviewBar analysis template selection', () => {
  it('renders a template selector with Evaluation Criteria as the default', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByText('Analysis Template')).toBeInTheDocument();
    expect(screen.getByText('Evaluation Criteria')).toBeInTheDocument();
  });

  it('passes the selected template to onRunAnalysis when Run Analysis is clicked', async () => {
    const onRunAnalysis = vi.fn();
    render(<DiscoveryOverviewBar {...defaultProps} onRunAnalysis={onRunAnalysis} />);

    await userEvent.click(screen.getByRole('button', { name: /run ai analysis/i }));
    expect(onRunAnalysis).toHaveBeenCalledWith('evaluation_criteria');
  });
});
