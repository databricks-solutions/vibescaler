// @spec RUBRIC_SPEC
// @req Invalid judge type in suggestions defaults to likert
import { describe, expect, it, vi, beforeEach, beforeAll } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RubricSuggestionPanel } from './RubricSuggestionPanel';

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

vi.mock('@/hooks/useWorkshopApi', () => ({
  useAvailableModels: () => ({
    data: [{ name: 'databricks-claude-opus-4-5', state: 'READY', task: 'llm/v1/chat' }],
  }),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

const renderPanel = () =>
  render(
    <RubricSuggestionPanel
      workshopId="ws-1"
      onAcceptSuggestion={vi.fn()}
      onClose={vi.fn()}
    />
  );

const generateSuggestions = async (suggestions: unknown[]) => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify(suggestions), { status: 200 })
  );
  renderPanel();
  fireEvent.click(screen.getByRole('button', { name: 'Generate' }));
  await screen.findByText('Add to Rubric');
};

describe('@spec:RUBRIC_SPEC RubricSuggestionPanel', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.clearAllMocks();
  });

  it('normalizes freeform suggestions from the API to likert', async () => {
    await generateSuggestions([
      { title: 'Criterion A', description: 'Some description here', judgeType: 'freeform' },
    ]);

    expect(screen.getByText('likert')).toBeInTheDocument();
    expect(screen.queryByText('freeform')).not.toBeInTheDocument();
  });

  it('toggles judge type between likert and binary only, never freeform', async () => {
    await generateSuggestions([
      { title: 'Criterion A', description: 'Some description here', judgeType: 'likert' },
    ]);

    const badge = screen.getByText('likert');
    fireEvent.click(badge);
    expect(screen.getByText('binary')).toBeInTheDocument();

    fireEvent.click(screen.getByText('binary'));
    expect(screen.getByText('likert')).toBeInTheDocument();
    expect(screen.queryByText('freeform')).not.toBeInTheDocument();
  });

  it('renders multi-line suggestion text with preserved newlines', async () => {
    await generateSuggestions([
      {
        title: 'Criterion A',
        description: 'Line 1\nLine 2',
        positive: 'Pos 1\nPos 2',
        negative: 'Neg 1\nNeg 2',
        examples: 'Ex 1\nEx 2',
        judgeType: 'binary',
      },
    ]);

    const description = screen.getByText(/Line 1/);
    expect(description.textContent).toBe('Line 1\nLine 2');
    expect(description).toHaveClass('whitespace-pre-wrap');

    expect(screen.getByText(/Pos 1/)).toHaveClass('whitespace-pre-wrap');
    expect(screen.getByText(/Neg 1/)).toHaveClass('whitespace-pre-wrap');
    expect(screen.getByText(/Ex 1/)).toHaveClass('whitespace-pre-wrap');
  });
});
