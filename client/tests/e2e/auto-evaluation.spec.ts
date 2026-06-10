/**
 * E2E Tests for Auto-Evaluation setup (annotation start page)
 *
 * Spec: JUDGE_EVALUATION_SPEC (Auto-Evaluation section)
 *
 * These tests drive the facilitator UI: sidebar navigation to the annotation
 * start page, the auto-evaluation toggle + model selector, and starting the
 * annotation phase with auto-evaluation disabled.
 *
 * Running auto-evaluation itself (background MLflow job) requires Databricks
 * model serving and is covered by unit tests
 * (tests/unit/routers/test_workshops_begin_annotation.py); rendering of
 * evaluation results in the Judge Tuning page is covered by
 * judge-evaluation.spec.ts via the demo-model pipeline.
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';

const MOCK_MODELS = [
  { name: 'databricks-claude-opus-4-5', state: 'READY', task: 'llm/v1/chat' },
  { name: 'databricks-gpt-5-2', state: 'READY', task: 'llm/v1/chat' },
];

test.describe('Auto-Evaluation Setup', () => {
  test('annotation setup page offers auto-evaluation toggle and model selection', {
    tag: [
      '@spec:JUDGE_EVALUATION_SPEC',
      '@req:Facilitator can toggle auto-evaluation and select a model at annotation start',
    ],
  }, async ({ page }) => {
    // Model list comes from Databricks serving endpoints; mock it so the
    // dropdown is deterministic in the e2e environment.
    await page.route('**/available-models', (route) => route.fulfill({ json: MOCK_MODELS }));

    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Auto-Eval Setup Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(3)
      .withDiscoveryFinding({ insight: 'Test finding for rubric' })
      .withDiscoveryComplete()
      .withRubric({ question: 'Response Quality: Is the response helpful?' })
      .withRealApi()
      .inPhase('rubric')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    const workshopHeading = page.getByRole('heading', { name: 'Auto-Eval Setup Workshop' });
    await expect(workshopHeading).toBeVisible({ timeout: 10000 });
    await workshopHeading.click();

    // Navigate to the annotation phase via the workflow sidebar; annotation
    // has not started, so the facilitator lands on the setup page.
    await page.getByTestId('workflow-step-annotation').click();
    await expect(page.getByRole('heading', { name: 'Start Annotation Phase' })).toBeVisible({
      timeout: 10000,
    });

    // Auto-evaluation section with toggle, enabled by default
    await expect(page.getByText('LLM Auto-Evaluation')).toBeVisible();
    const autoEvalToggle = page.locator('#auto-evaluate-toggle');
    await expect(autoEvalToggle).toBeVisible();
    await expect(autoEvalToggle).toHaveAttribute('aria-checked', 'true');

    // Model selector lists the available evaluation models (friendly names)
    await expect(page.getByText('Evaluation Model')).toBeVisible();
    await page.getByRole('combobox').click();
    await expect(page.getByRole('option', { name: 'Claude Opus 4.5' })).toBeVisible();
    await expect(page.getByRole('option', { name: 'GPT-5.2' })).toBeVisible();
    await page.keyboard.press('Escape');

    // Toggling off hides model selection and explains the manual path
    await autoEvalToggle.click();
    await expect(autoEvalToggle).toHaveAttribute('aria-checked', 'false');
    await expect(page.getByText(/Auto-evaluation disabled/)).toBeVisible();
    await expect(page.getByText('Evaluation Model')).toBeHidden();

    await scenario.cleanup();
  });

  test('annotation phase starts without auto-evaluation when toggle is off', {
    tag: [
      '@spec:JUDGE_EVALUATION_SPEC',
      '@req:Annotation phase can start with auto-evaluation disabled',
    ],
  }, async ({ page }) => {
    // Spec: evaluation_model_name=null skips auto-evaluation
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'No Auto-Eval Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withDiscoveryFinding({ insight: 'Finding' })
      .withDiscoveryComplete()
      .withRubric({ question: 'Quality: Is it good?' })
      .withRealApi()
      .inPhase('rubric')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    const workshopHeading = page.getByRole('heading', { name: 'No Auto-Eval Workshop' });
    await expect(workshopHeading).toBeVisible({ timeout: 10000 });
    await workshopHeading.click();

    await page.getByTestId('workflow-step-annotation').click();
    await expect(page.getByRole('heading', { name: 'Start Annotation Phase' })).toBeVisible({
      timeout: 10000,
    });

    // Disable auto-evaluation, then start the phase through the UI
    const autoEvalToggle = page.locator('#auto-evaluate-toggle');
    await autoEvalToggle.click();
    await expect(autoEvalToggle).toHaveAttribute('aria-checked', 'false');

    await page.getByRole('button', { name: 'Start Annotation Phase' }).click();

    // Success toast for the no-auto-eval path (not the MLflow warning path)
    await expect(page.getByText('Annotation started')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('SMEs can now begin rating traces.')).toBeVisible();

    // Facilitator is moved to the annotation monitor
    await expect(page.getByRole('heading', { name: 'Annotation Monitoring' })).toBeVisible({
      timeout: 15000,
    });

    // Backend actually advanced the phase
    const workshop = await scenario.api.getWorkshop();
    expect(workshop.current_phase).toBe('annotation');

    await scenario.cleanup();
  });
});
