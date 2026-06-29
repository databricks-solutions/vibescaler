// @spec DISCOVERY_SPEC
// @req Overview bar shows stats inline + compact controls (Run Analysis, Add Traces, Pause, Model selector)
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { DiscoveryOverviewBar } from './DiscoveryOverviewBar';

// Polyfill pointer-capture and scrollIntoView for Radix UI in jsdom
beforeAll(() => {
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.hasPointerCapture = Element.prototype.hasPointerCapture || (() => false);
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.setPointerCapture = Element.prototype.setPointerCapture || vi.fn();
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.releasePointerCapture = Element.prototype.releasePointerCapture || vi.fn();
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.scrollIntoView = Element.prototype.scrollIntoView || vi.fn();
});

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
    discoveryMode: 'analysis' as const,
    followupsEnabled: true,
    onModeChange: vi.fn(),
    onFollowupsToggle: vi.fn(),
    canManageDiscovery: true,
  };

  const getSettingsTrigger = () =>
    screen
      .getAllByRole('button')
      .find((button) => button.getAttribute('aria-haspopup') === 'menu') as HTMLButtonElement;

  it('renders inline stats', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByText(/4 participants/)).toBeInTheDocument();
    expect(screen.getByText(/10 active traces/)).toBeInTheDocument();
    expect(screen.getByText(/28 feedback items/)).toBeInTheDocument();
  });

  it('runs analysis with the selected template from the Run AI Analysis button', async () => {
    const onRunAnalysis = vi.fn();
    render(<DiscoveryOverviewBar {...defaultProps} onRunAnalysis={onRunAnalysis} />);
    await userEvent.click(screen.getByRole('button', { name: /run ai analysis/i }));
    expect(onRunAnalysis).toHaveBeenCalledWith('evaluation_criteria');
  });

  it('disables Run AI Analysis when mlflow not configured', () => {
    render(<DiscoveryOverviewBar {...defaultProps} hasMlflowConfig={false} />);
    expect(screen.getByRole('button', { name: /run ai analysis/i })).toBeDisabled();
  });

  it('shows Pause/Resume toggle', () => {
    render(<DiscoveryOverviewBar {...defaultProps} />);
    expect(screen.getByRole('button', { name: /pause phase/i })).toBeInTheDocument();
  });

  it('exposes mode and follow-ups controls in the settings dropdown', async () => {
    const onModeChange = vi.fn();
    const onFollowupsToggle = vi.fn();
    render(
      <DiscoveryOverviewBar
        {...defaultProps}
        onModeChange={onModeChange}
        onFollowupsToggle={onFollowupsToggle}
      />
    );

    await userEvent.click(getSettingsTrigger());

    expect(screen.getByText('Workspace Settings')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Social' }));
    expect(onModeChange).toHaveBeenCalledWith('social');

    await userEvent.click(screen.getByRole('button', { name: /toggle follow-ups/i }));
    expect(onFollowupsToggle).toHaveBeenCalled();
  });

  it('disables management controls when canManageDiscovery is false', () => {
    render(<DiscoveryOverviewBar {...defaultProps} canManageDiscovery={false} />);
    expect(getSettingsTrigger()).toBeDisabled();
    expect(screen.getByRole('button', { name: /add traces/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /pause phase/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /run ai analysis/i })).toBeDisabled();
  });
});
