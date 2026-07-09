// @spec DISCOVERY_SPEC
// @req Disagreements color-coded by priority (red/yellow/blue) on trace cards
// Regression guard: DiscoveryTraceCard once rendered every disagreement priority
// in the same rose styling. These tests require three DISTINCT per-priority
// classes (red = high, yellow = medium, blue = lower) and fail on any
// single-color rendering.
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DiscoveryTraceCard } from './DiscoveryTraceCard';

const mockTrace = {
  id: 'trace-1',
  workshop_id: 'ws-1',
  input: '{"messages":[{"role":"user","content":"What is the capital of France?"}]}',
  output: '{"choices":[{"message":{"content":"The capital of France is Paris."}}]}',
};

function makeDisagreement(priority: string, summary: string) {
  return {
    trace_id: 'trace-1',
    summary,
    underlying_theme: `Theme for ${priority}`,
    followup_questions: [],
    facilitator_suggestions: [],
    priority,
  };
}

const mockDisagreements = [
  makeDisagreement('high', 'HIGH priority disagreement'),
  makeDisagreement('medium', 'MEDIUM priority disagreement'),
  makeDisagreement('lower', 'LOWER priority disagreement'),
];

function renderCard() {
  return render(
    <DiscoveryTraceCard
      trace={mockTrace}
      feedback={[]}
      disagreements={mockDisagreements}
      onPromote={vi.fn()}
    />
  );
}

function cardFor(summary: RegExp): HTMLElement {
  const el = screen.getByText(summary).closest('.rounded-xl.border');
  expect(el).not.toBeNull();
  return el as HTMLElement;
}

describe('DiscoveryTraceCard - disagreement color-coding by priority', () => {
  it('HIGH disagreement card uses red border and background', () => {
    renderCard();
    const card = cardFor(/HIGH priority disagreement/);
    expect(card.className).toContain('border-red-200');
    expect(card.className).toContain('bg-red-50');
  });

  it('MEDIUM disagreement card uses yellow border and background', () => {
    renderCard();
    const card = cardFor(/MEDIUM priority disagreement/);
    expect(card.className).toContain('border-yellow-200');
    expect(card.className).toContain('bg-yellow-50');
  });

  it('LOWER disagreement card uses blue border and background', () => {
    renderCard();
    const card = cardFor(/LOWER priority disagreement/);
    expect(card.className).toContain('border-blue-200');
    expect(card.className).toContain('bg-blue-50');
  });

  it('the three priorities render with three distinct color classes (not all one color)', () => {
    renderCard();
    const high = cardFor(/HIGH priority disagreement/);
    const medium = cardFor(/MEDIUM priority disagreement/);
    const lower = cardFor(/LOWER priority disagreement/);
    expect(high.className).not.toEqual(medium.className);
    expect(medium.className).not.toEqual(lower.className);
    expect(high.className).not.toEqual(lower.className);
    // No card may fall back to the old uniform rose styling
    for (const card of [high, medium, lower]) {
      expect(card.className).not.toContain('rose');
    }
  });

  it('priority tier labels are distinct (High/Medium/Lower Disagreement)', () => {
    renderCard();
    expect(screen.getByText('High Disagreement')).toBeInTheDocument();
    expect(screen.getByText('Medium Disagreement')).toBeInTheDocument();
    expect(screen.getByText('Lower Disagreement')).toBeInTheDocument();
  });
});
