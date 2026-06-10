/**
 * E2E Tests for Per-Question Judge Type in Rubrics
 *
 * Spec: RUBRIC_SPEC (Per-Question Judge Type / Scale Rendering)
 *
 * Tests that binary vs likert questions render the correct UI controls
 * during annotation. AnnotationDemo renders:
 * - Likert questions as five div[role="button"] controls labeled 1-5
 * - Binary questions as two div[role="button"] controls labeled Pass / Fail
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';
import { waitForAnnotationInterface } from '../lib/actions/annotation';

// Declare process.env for TypeScript
declare const process: { env: Record<string, string | undefined> };

const API_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';

/** Likert rating controls: role=button elements whose text is exactly 1-5. */
const likertControl = (page: import('@playwright/test').Page, value: number) =>
  page.locator('[role="button"]').filter({ hasText: new RegExp(`^${value}$`) }).first();

/** Binary rating controls: role=button elements labeled Pass / Fail. */
const binaryControl = (page: import('@playwright/test').Page, label: 'Pass' | 'Fail') =>
  page.locator('[role="button"]').filter({ hasText: new RegExp(`^${label}$`) }).first();

test.describe('Per-Question Judge Type', () => {
  test('likert questions show 1-5 rating controls', {
    tag: ['@spec:RUBRIC_SPEC', '@req:Likert scale shows 1-5 rating options'],
  }, async ({ page }) => {
    // Spec: RUBRIC_SPEC (Scale Rendering)
    // Likert questions must display all five rating options, and no Pass/Fail buttons.
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Likert Rating Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(2)
      .withRubric({
        question: 'Quality: Rate the response quality from 1-5',
        judgeType: 'likert',
      })
      .inPhase('annotation')
      .withRealApi()
      .build();

    await page.goto(`/?workshop=${scenario.workshop.id}`);
    await scenario.loginAs(scenario.users.sme[0]);
    await waitForAnnotationInterface(page);

    // All five likert rating controls must be present
    for (const value of [1, 2, 3, 4, 5]) {
      await expect(likertControl(page, value)).toBeVisible({ timeout: 10000 });
    }

    // And a likert-only rubric must NOT render binary Pass/Fail controls
    await expect(page.locator('[role="button"]').filter({ hasText: /^Pass$/ })).toHaveCount(0);
    await expect(page.locator('[role="button"]').filter({ hasText: /^Fail$/ })).toHaveCount(0);

    await scenario.cleanup();
  });

  test('binary questions show Pass/Fail buttons (not stars)', {
    tag: ['@spec:RUBRIC_SPEC', '@req:Binary scale shows Pass/Fail buttons (not star ratings)'],
  }, async ({ page }) => {
    // Spec: RUBRIC_SPEC (Scale Rendering, Test 3)
    // Binary questions must show Pass/Fail buttons and no 1-5 rating controls.
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Binary Rating Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(2)
      .withRubric({
        question: 'Accuracy: Is the response correct?|||JUDGE_TYPE|||binary',
        judgeType: 'binary',
      })
      .inPhase('annotation')
      .withRealApi()
      .build();

    await page.goto(`/?workshop=${scenario.workshop.id}`);
    await scenario.loginAs(scenario.users.sme[0]);
    await waitForAnnotationInterface(page);

    // Pass and Fail controls must be present
    await expect(binaryControl(page, 'Pass')).toBeVisible({ timeout: 10000 });
    await expect(binaryControl(page, 'Fail')).toBeVisible();

    // A binary-only rubric must NOT render likert numeric rating controls
    for (const value of [1, 2, 3, 4, 5]) {
      await expect(
        page.locator('[role="button"]').filter({ hasText: new RegExp(`^${value}$`) })
      ).toHaveCount(0);
    }

    await scenario.cleanup();
  });

  test('mixed rubric renders correct controls per question', {
    tag: ['@spec:RUBRIC_SPEC', '@req:Mixed rubrics support different scales per question'],
  }, async ({ page }) => {
    // Spec: RUBRIC_SPEC (Tests 4 & 5)
    // A mixed rubric must render binary controls for the binary question AND
    // likert controls for the likert question on the same page.
    const mixedQuestion = [
      'Accuracy: Is the response factually correct?|||JUDGE_TYPE|||binary',
      'Helpfulness: Rate helpfulness 1-5|||JUDGE_TYPE|||likert',
    ].join('|||QUESTION_SEPARATOR|||');

    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Mixed Rubric Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(2)
      .withRubric({ question: mixedQuestion, judgeType: 'likert' })
      .inPhase('annotation')
      .withRealApi()
      .build();

    await page.goto(`/?workshop=${scenario.workshop.id}`);
    await scenario.loginAs(scenario.users.sme[0]);
    await waitForAnnotationInterface(page);

    // Both question titles render
    await expect(page.getByText('Accuracy').first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Helpfulness').first()).toBeVisible();

    // The binary question contributes Pass/Fail controls
    await expect(binaryControl(page, 'Pass')).toBeVisible();
    await expect(binaryControl(page, 'Fail')).toBeVisible();

    // The likert question contributes all five 1-5 controls
    for (const value of [1, 2, 3, 4, 5]) {
      await expect(likertControl(page, value)).toBeVisible();
    }

    await scenario.cleanup();
  });

  test('default judge type is likert when not specified', {
    tag: ['@spec:RUBRIC_SPEC', '@req:Rubric persists and is retrievable via GET after creation'],
  }, async ({ page, request }) => {
    // Spec: RUBRIC_SPEC (Per-Question Judge Type: default to likert; CRUD Lifecycle)
    const runId = `${Date.now()}`;

    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: `Default Judge Type Test ${runId}` })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withDiscoveryFinding({ insight: 'Test finding' })
      .withDiscoveryComplete()
      .withRealApi()
      .inPhase('rubric')
      .build();

    const workshopId = scenario.workshop.id;
    const facilitatorId = scenario.facilitator.id;

    // Create rubric WITHOUT specifying judge type (should default to likert)
    const rubricResponse = await request.post(`${API_URL}/workshops/${workshopId}/rubric`, {
      data: {
        question: 'Quality: Is the response high quality?',
        created_by: facilitatorId,
        // Note: No judge_type specified
      },
    });

    expect(rubricResponse.ok()).toBeTruthy();

    // Fetch the rubric back and verify it persisted with the likert default
    const getRubricResponse = await request.get(`${API_URL}/workshops/${workshopId}/rubric`);
    expect(getRubricResponse.ok()).toBeTruthy();

    const rubric = await getRubricResponse.json() as { question?: string; judge_type?: string };
    expect(rubric.question).toBe('Quality: Is the response high quality?');
    expect(rubric.judge_type).toBe('likert');

    await scenario.cleanup();
  });
});

test.describe('Binary Scale Feedback Storage', () => {
  // NOTE: deliberately NOT tagged to "Binary feedback logged as 0/1 to MLflow (not 3)".
  // This test never inspects MLflow — it verifies the workshop API stores binary
  // ratings as 0/1. The MLflow side of that criterion is covered by
  // tests/unit/services/test_rubric_lifecycle.py::TestBinaryFeedbackLoggedAsZeroOne,
  // which asserts the value passed to mlflow.log_feedback.
  test('binary annotation rating stored as 0/1 via workshop API', {
    tag: ['@spec:RUBRIC_SPEC'],
  }, async ({ page, request }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Binary Feedback Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(1)
      .withRubric({
        question: 'Correct: Is this correct?|||JUDGE_TYPE|||binary',
        judgeType: 'binary',
      })
      .inPhase('annotation')
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const smeId = scenario.users.sme[0].id;

    // Get traces assigned to the SME
    const tracesResp = await request.get(`${API_URL}/workshops/${workshopId}/traces?user_id=${smeId}`);
    expect(tracesResp.ok()).toBeTruthy();
    const traces = await tracesResp.json() as Array<{ id: string }>;
    expect(traces.length).toBeGreaterThan(0);

    // Submit a binary annotation (Pass = 1)
    const annotationResp = await request.post(`${API_URL}/workshops/${workshopId}/annotations`, {
      data: {
        trace_id: traces[0].id,
        user_id: smeId,
        rating: 1,
        ratings: { q_1: 1 },
      },
    });
    expect(annotationResp.ok()).toBeTruthy();

    // Fetch annotations and verify the per-question binary rating is stored verbatim
    const getAnnotationsResp = await request.get(`${API_URL}/workshops/${workshopId}/annotations`);
    expect(getAnnotationsResp.ok()).toBeTruthy();
    const annotations = await getAnnotationsResp.json() as Array<{
      ratings?: Record<string, number>;
    }>;
    expect(annotations.length).toBeGreaterThan(0);
    expect(annotations[0].ratings?.q_1).toBe(1);

    await scenario.cleanup();
  });
});
