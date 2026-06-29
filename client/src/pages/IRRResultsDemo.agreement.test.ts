// @spec JUDGE_EVALUATION_SPEC

import { describe, expect, it } from 'vitest';
import { calculateRealTraceAgreement } from './IRRResultsDemo';
import type { Trace } from '@/client';

type AnnotationInput = Parameters<typeof calculateRealTraceAgreement>[1];

const trace = (id: string) => ({ id }) as Trace;

const ann = (
  traceId: string,
  userId: string,
  rating: number,
  ratings: Record<string, number> | null = null,
) =>
  ({
    id: `${traceId}:${userId}`,
    workshop_id: 'w1',
    trace_id: traceId,
    user_id: userId,
    rating,
    ratings,
    user_name: userId,
    user_email: `${userId}@example.com`,
    user_role: 'participant',
  }) as unknown as AnnotationInput[number];

describe('calculateRealTraceAgreement', () => {
  it('only counts annotators who rated the requested metric (no legacy fallback)', () => {
    // u3 never rated q1; their legacy rating of 5 previously inflated sigma
    // past the 1.5 high-disagreement threshold despite perfect q1 agreement
    const annotations = [
      ann('t1', 'u1', 1, { q1: 1 }),
      ann('t1', 'u2', 1, { q1: 1 }),
      ann('t1', 'u3', 5, { q2: 5 }),
    ];
    const result = calculateRealTraceAgreement([trace('t1')], annotations, 'q1');
    expect(result.t1.ratingCount).toBe(2);
    expect(result.t1.agreement).toBe(0);
  });

  it('excludes traces with fewer than two ratings for the requested metric', () => {
    const annotations = [
      ann('t1', 'u1', 1, { q1: 1 }),
      ann('t1', 'u2', 3, { q2: 3 }),
    ];
    const result = calculateRealTraceAgreement([trace('t1')], annotations, 'q1');
    expect(result.t1).toBeUndefined();
  });

  it('still reports high disagreement when ratings genuinely diverge', () => {
    const annotations = [
      ann('t1', 'u1', 1, { q1: 1 }),
      ann('t1', 'u2', 5, { q1: 5 }),
    ];
    const result = calculateRealTraceAgreement([trace('t1')], annotations, 'q1');
    expect(result.t1.agreement).toBe(2);
    expect(result.t1.agreement).toBeGreaterThan(1.5);
  });

  it('uses the legacy rating field when no metric is requested', () => {
    const annotations = [ann('t1', 'u1', 2), ann('t1', 'u2', 4)];
    const result = calculateRealTraceAgreement([trace('t1')], annotations, null);
    expect(result.t1.ratingCount).toBe(2);
    expect(result.t1.agreement).toBe(1);
  });
});
