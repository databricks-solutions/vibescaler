/**
 * E2E tests for trace visibility across selections and sessions.
 *
 * Verifies that participants only see traces in the active discovery
 * selection, traces dropped from the selection are hidden (not deleted),
 * and annotation order persists across page reload.
 *
 * @spec DISCOVERY_SPEC
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';

const API_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';

// Declare process for env var access
declare const process: { env: Record<string, string | undefined> };

test.describe('Trace Visibility', {
  tag: ['@spec:DISCOVERY_SPEC'],
}, () => {
  test('participant sees only current round traces', {
    tag: ['@spec:DISCOVERY_SPEC', '@req:Participants only see traces in the current active discovery trace list'],
  }, async ({ page }) => {
    // Create scenario with discovery phase and specific traces
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Current Round Traces' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(5)
      .inPhase('discovery')
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const participant = scenario.users.participant[0];
    const allTraces = scenario.traces;

    // Verify participant can see discovery traces via API
    const discResp = await page.request.get(
      `${API_URL}/workshops/${workshopId}/traces?user_id=${participant.id}`
    );
    expect(discResp.ok()).toBeTruthy();

    const visibleTraces = (await discResp.json()) as Array<{ id: string }>;
    const visibleIds = visibleTraces.map((t) => t.id);

    // All 5 traces from the active selection should be visible — and nothing else
    for (const trace of allTraces) {
      expect(visibleIds).toContain(trace.id);
    }
    expect(visibleTraces.length).toBe(allTraces.length);

    await scenario.cleanup();
  });

  test('old traces hidden after discovery selection changes', {
    tag: ['@spec:DISCOVERY_SPEC', '@req:Traces outside the active discovery selection are hidden from participants but not deleted'],
  }, async ({ page }) => {
    // Create scenario with discovery phase (active selection = 3 traces)
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Round Change Visibility' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(3)
      .inPhase('discovery')
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const participant = scenario.users.participant[0];

    // Verify the initial 3 active traces are visible
    const r1Resp = await page.request.get(
      `${API_URL}/workshops/${workshopId}/traces?user_id=${participant.id}`
    );
    expect(r1Resp.ok()).toBeTruthy();
    const r1Traces = (await r1Resp.json()) as Array<{ id: string }>;
    expect(r1Traces.length).toBe(3);

    // Upload two more traces (workshop now holds 5 traces total)
    const newTracesResp = await page.request.post(
      `${API_URL}/workshops/${workshopId}/traces`,
      {
        headers: { 'Content-Type': 'application/json' },
        data: [
          { input: 'New round question 1', output: 'New round answer 1' },
          { input: 'New round question 2', output: 'New round answer 2' },
        ],
      }
    );
    expect(newTracesResp.ok()).toBeTruthy();

    // Reset discovery (clears the active selection), then start discovery
    // again with a limit of 2 — the new active selection is a strict subset.
    const resetResp = await page.request.post(
      `${API_URL}/workshops/${workshopId}/reset-discovery`
    );
    expect(resetResp.ok()).toBeTruthy();

    const beginResp = await page.request.post(
      `${API_URL}/workshops/${workshopId}/begin-discovery?trace_limit=2`
    );
    expect(beginResp.ok()).toBeTruthy();

    // Participant now sees ONLY the 2 traces in the new active selection
    const r2Resp = await page.request.get(
      `${API_URL}/workshops/${workshopId}/traces?user_id=${participant.id}`
    );
    expect(r2Resp.ok()).toBeTruthy();
    const r2Traces = (await r2Resp.json()) as Array<{ id: string }>;
    expect(r2Traces.length).toBe(2);

    // Hidden traces are NOT deleted — all 5 remain retrievable via all-traces
    const allResp = await page.request.get(
      `${API_URL}/workshops/${workshopId}/all-traces`
    );
    expect(allResp.ok()).toBeTruthy();
    const allTraces = (await allResp.json()) as Array<{ id: string }>;
    expect(allTraces.length).toBe(5);

    // Exactly 3 traces are hidden from the participant view
    const visibleIds = new Set(r2Traces.map((t) => t.id));
    const hiddenIds = allTraces.map((t) => t.id).filter((id) => !visibleIds.has(id));
    expect(hiddenIds.length).toBe(3);

    await scenario.cleanup();
  });

  test('annotation order persistent across reload', {
    tag: ['@spec:DISCOVERY_SPEC', '@req:Annotation trace order is deterministic per user and persists across page reloads'],
  }, async ({ page }) => {
    // Create scenario with annotation phase and randomization enabled
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Persistent Order Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(8)
      .withRubric({ question: 'Rate this response' })
      .inPhase('annotation')
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const sme = scenario.users.sme[0];

    // Enable randomization by re-starting annotation phase with randomize=true
    await page.request.post(
      `${API_URL}/workshops/${workshopId}/begin-annotation`,
      {
        headers: { 'Content-Type': 'application/json' },
        data: { randomize: true, trace_limit: -1 },
      }
    );

    // Fetch trace order first time
    const resp1 = await page.request.get(
      `${API_URL}/workshops/${workshopId}/traces?user_id=${sme.id}`
    );
    expect(resp1.ok()).toBeTruthy();
    const order1 = ((await resp1.json()) as Array<{ id: string }>).map(
      (t) => t.id
    );

    // Simulate page reload by fetching again
    const resp2 = await page.request.get(
      `${API_URL}/workshops/${workshopId}/traces?user_id=${sme.id}`
    );
    expect(resp2.ok()).toBeTruthy();
    const order2 = ((await resp2.json()) as Array<{ id: string }>).map(
      (t) => t.id
    );

    // Order should be identical across requests (deterministic per user)
    expect(order1).toEqual(order2);

    await scenario.cleanup();
  });
});
