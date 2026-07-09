// @spec DISCOVERY_SPEC
// @req Overview bar shows stats inline + compact controls (Run Analysis, Add Traces, Pause, Model selector)
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { DiscoveryOverviewBar } from './DiscoveryOverviewBar';

describe('DiscoveryOverviewBar', () => {
  const defaultProps = {
    participantCount: 4,
    traceCount: 10,
    feedbackCount: 28,
    currentModel: 'Claude Sonnet 4.5',
    modelOptions: [
      { value: 'Claude Sonnet 4.5', label: 'Claude Sonnet 4.5', disabled: false },
      { value: 'demo', label: 'Demo Mode', disabled: false },
    ],
    onRunAnalysis: vi.fn(),
    onModelChange: vi.fn(),
    onPauseToggle: vi.fn(),
    onAddTraces: vi.fn(),
    isPaused: false,
    isAnalysisRunning: false,
    hasMlflowConfig: true,
  };

  // AUDIT (2026-06): assertions updated to the live overview bar labels — this file
  // was failing (stale "10 traces"/"28 findings"/"Run Analysis" expectations) while
  // still minting coverage for the overview-bar criterion.
  it('renders inline stats', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByText(/4 participants/)).toBeInTheDocument();
    expect(screen.getByText(/10 active traces/)).toBeInTheDocument();
    expect(screen.getByText(/28 feedback items/)).toBeInTheDocument();
  });

  it('renders Run Analysis button', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByRole('button', { name: /run ai analysis/i })).toBeInTheDocument();
  });

  it('disables Run Analysis when mlflow not configured', () => {
    render(<DiscoveryOverviewBar {...defaultProps} hasMlflowConfig={false} />);
    expect(screen.getByRole('button', { name: /run ai analysis/i })).toBeDisabled();
  });

  it('shows Pause/Resume toggle', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
  });
});
