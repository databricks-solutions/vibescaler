/**
 * E2E Test: Discovery Analysis (Step 2 — Findings Synthesis)
 *
 * Tests the facilitator's ability to run AI analysis on discovery feedback and
 * see the results in the FacilitatorDiscoveryWorkspace (analysis controls in the
 * overview bar, cross-trace findings in the summary section, trace-specific
 * findings/disagreements on trace cards).
 *
 * Uses mocked API — the analysis endpoints return deterministic mock data.
 *
 * AUDIT (2026-06): this file previously navigated via "View All Findings" /
 * an "Analysis" tab (FindingsReviewPage), which no longer exists. Every
 * assertion was wrapped in `if (await x.isVisible())` guards that never fired,
 * so the tests passed vacuously. Rewritten with unconditional assertions
 * against the live workspace.
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib/scenario-builder';
import { WorkshopPhase } from '../lib/types';

test.describe('Discovery Analysis (Step 2)', {
  tag: ['@spec:DISCOVERY_SPEC'],
}, () => {

  test('facilitator sees analysis controls with template and model selectors', {
    tag: [
      '@spec:DISCOVERY_SPEC',
      '@req:Facilitator selects analysis template (Evaluation Criteria or Themes & Patterns) before running',
    ],
  }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Analysis Controls Test' })
      .withFacilitator()
      .withParticipants(2)
      .withTraces(3)
      .inPhase(WorkshopPhase.DISCOVERY)
      .build();

    await scenario.loginAs(scenario.facilitator);

    // The facilitator lands on FacilitatorDiscoveryWorkspace; the overview bar
    // exposes the analysis controls.
    await expect(page.getByText('Analysis Template')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Evaluation Criteria')).toBeVisible();
    await expect(page.getByTestId('model-selector')).toBeVisible();
    await expect(page.getByRole('button', { name: /Run AI Analysis/i })).toBeVisible();

    await scenario.cleanup();
  });

  test('facilitator triggers analysis and sees results with findings and disagreements', {
    tag: [
      '@spec:DISCOVERY_SPEC',
      '@req:Facilitator can trigger analysis at any time (even partial feedback)',
    ],
  }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Analysis Results Test' })
      .withFacilitator()
      .withParticipants(2)
      .withTraces(3)
      .inPhase(WorkshopPhase.DISCOVERY)
      .build();

    // The shared api-mocker has no route for available-models; the workspace
    // disables Run Analysis when no models are available, so serve one here.
    await page.route(/\/workshops\/[^/?]+\/available-models$/, (route) =>
      route.fulfill({
        json: [{ name: 'databricks-claude-sonnet-4-5', state: 'READY', task: 'llm/v1/chat' }],
      }),
    );

    await scenario.loginAs(scenario.facilitator);

    // Run analysis from the overview bar
    const runButton = page.getByRole('button', { name: /Run AI Analysis/i });
    await expect(runButton).toBeVisible({ timeout: 10000 });
    await expect(runButton).toBeEnabled();
    await runButton.click();

    // Cross-trace finding (2 evidence traces) appears in the summary section
    await expect(page.getByText('Responses should include specific references')).toBeVisible({ timeout: 10000 });

    // Trace-specific finding (1 evidence trace) appears on its trace card
    await expect(page.getByText('Tone is generally appropriate')).toBeVisible();

    // HIGH-priority disagreement is rendered (trace card and/or summary section)
    await expect(page.getByText('Rating split: GOOD vs BAD').first()).toBeVisible();

    await scenario.cleanup();
  });

  // NOTE (2026-06 audit): the previous "running analysis multiple times preserves
  // history in dropdown" test was removed. It was vacuous (guarded on a navigation
  // path that no longer exists) and the live workspace has no analysis-history UI
  // to assert against. The criterion "Each analysis run creates a new record
  // (history preserved)" remains covered by backend tests
  // (tests/unit/routers/test_discovery_analysis.py,
  // tests/unit/services/test_discovery_analysis_service.py).

  // NOTE (2026-06 audit): deliberately untagged + skipped so it cannot count as spec
  // coverage. The live FacilitatorDiscoveryWorkspace does not render a <2-participant
  // warning (regression, owner decision pending). Re-enable and re-tag to
  // "Warning if < 2 participants (not an error)" once the warning is restored.
  test.skip('analysis results show participant warning when < 2 participants', async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Warning Test' })
      .withFacilitator()
      .withParticipants(1) // only 1 participant
      .withTraces(2)
      .inPhase(WorkshopPhase.DISCOVERY)
      .build();

    await scenario.loginAs(scenario.facilitator);

    const runButton = page.getByRole('button', { name: /Run AI Analysis/i });
    await expect(runButton).toBeVisible({ timeout: 10000 });
    await runButton.click();

    // Should show warning (not error) about limited participant data
    await expect(page.getByText('Limited Participant Data')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/1 participant/).first()).toBeVisible();

    await scenario.cleanup();
  });
});
