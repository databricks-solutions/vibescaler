/**
 * Test for bug: Last trace annotation cannot be saved
 *
 * Bug report: Multiple annotators labeling 10 traces report that the last one
 * cannot be saved. Facilitator sees 9/10 completed.
 *
 * These tests verify that all 10 annotations are saved correctly via API.
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';
import { WorkshopPhase } from '../lib/types';
import { submitAnnotationViaApi, getAnnotations, waitForAnnotationProgress } from '../lib/actions/annotation';

// This repo doesn't include Node typings in the client TS config; keep `process.env` without adding deps.
declare const process: { env: Record<string, string | undefined> };

const API_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';

test.describe('Annotation - Last Trace Bug', {
  tag: ['@spec:ANNOTATION_SPEC'],
}, () => {
  test('all 10 annotations should be saved when annotating via API', {
    tag: ['@spec:ANNOTATION_SPEC', '@req:Annotation count reflects unique submissions (not re-submissions)'],
  }, async ({
    page,
  }) => {
    // Create a real API scenario
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Last Trace Bug Test' })
      .withFacilitator()
      .withSMEs(2)
      .withTraces(10)
      .withRubric({ question: 'How helpful is this response?' })
      .inPhase(WorkshopPhase.ANNOTATION)
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const traces = scenario.traces;

    expect(traces.length).toBe(10);

    // Have each SME annotate all 10 traces via API
    for (const sme of scenario.users.sme) {
      for (let i = 0; i < traces.length; i++) {
        const trace = traces[i];
        await submitAnnotationViaApi(
          page,
          workshopId,
          {
            trace_id: trace.id,
            user_id: sme.id,
            rating: 4,
            comment: `Annotation from ${sme.name} for trace ${i + 1}`,
          },
          API_URL
        );
      }
    }

    // Verify all annotations were saved for each user
    for (const sme of scenario.users.sme) {
      const annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
      expect(annotations.length).toBe(10);

      // Verify we have annotations for all 10 traces
      const annotatedTraceIds = new Set(annotations.map((a) => a.trace_id));
      expect(annotatedTraceIds.size).toBe(10);
    }

    // Verify facilitator's view: all 10 traces should have annotations
    const allAnnotations = await getAnnotations(page, workshopId, undefined, API_URL);
    const tracesWithAnnotations = new Set(allAnnotations.map((a) => a.trace_id));

    // Key assertion - facilitator should see 10/10, not 9/10
    expect(tracesWithAnnotations.size).toBe(10);

    await scenario.cleanup();
  });

  test('10th trace annotation should be saved correctly', {
    tag: ['@spec:ANNOTATION_SPEC', '@req:Annotation upsert persists every trace submission, including the final trace in a session'],
  }, async ({ page }) => {
    // Create scenario with real API
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Tenth Trace Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(10)
      .withRubric({ question: 'How helpful is this response?' })
      .inPhase(WorkshopPhase.ANNOTATION)
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const sme = scenario.users.sme[0];
    const traces = scenario.traces;

    // Save annotations for traces 1-9
    for (let i = 0; i < 9; i++) {
      await submitAnnotationViaApi(
        page,
        workshopId,
        {
          trace_id: traces[i].id,
          user_id: sme.id,
          rating: 4,
        },
        API_URL
      );
    }

    // Verify 9 annotations exist
    let annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
    expect(annotations.length).toBe(9);

    // Now save the 10th annotation - this is the key test
    await submitAnnotationViaApi(
      page,
      workshopId,
      {
        trace_id: traces[9].id,
        user_id: sme.id,
        rating: 5,
        comment: 'The critical 10th annotation',
      },
      API_URL
    );

    // Verify all 10 annotations now exist
    annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
    expect(annotations.length).toBe(10);

    // Verify trace 10 specifically was saved
    const trace10Annotation = annotations.find((a) => a.trace_id === traces[9].id);
    expect(trace10Annotation).toBeDefined();
    expect(trace10Annotation!.rating).toBe(5);
    expect(trace10Annotation!.comment).toBe('The critical 10th annotation');

    await scenario.cleanup();
  });

  test('concurrent annotations from multiple users should all be saved', {
    tag: ['@spec:ANNOTATION_SPEC', '@req:Annotation count reflects unique submissions (not re-submissions)'],
  }, async ({
    page,
  }) => {
    // Create scenario with real API
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Concurrent Annotation Test' })
      .withFacilitator()
      .withSMEs(3)
      .withTraces(10)
      .withRubric({ question: 'How helpful is this response?' })
      .inPhase(WorkshopPhase.ANNOTATION)
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const traces = scenario.traces;
    const smes = scenario.users.sme;

    // All SMEs annotate all traces concurrently (simulated by interleaving)
    for (let i = 0; i < traces.length; i++) {
      // Each SME annotates trace i
      await Promise.all(
        smes.map((sme) =>
          submitAnnotationViaApi(
            page,
            workshopId,
            {
              trace_id: traces[i].id,
              user_id: sme.id,
              rating: (i % 5) + 1,
            },
            API_URL
          )
        )
      );
    }

    // Verify each SME has all 10 annotations
    for (const sme of smes) {
      const annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
      expect(annotations.length).toBe(10);
    }

    // Verify total annotation count
    const allAnnotations = await getAnnotations(page, workshopId, undefined, API_URL);
    expect(allAnnotations.length).toBe(30); // 3 SMEs * 10 traces

    await scenario.cleanup();
  });

  /**
   * UI LAST-TRACE PERSISTENCE TEST
   *
   * Drives all 10 annotations through the UI and clicks Complete on the last
   * trace. The final save is awaited before the terminal completion screen
   * (#155, data-testid="annotation-complete-screen") appears, so the 10th
   * annotation must be persisted server-side — not lost (the original bug
   * left the facilitator seeing 9/10).
   */
  test('UI: 10th annotation persists server-side after clicking Complete', {
    tag: ['@spec:ANNOTATION_SPEC', '@req:Completing the final trace shows a terminal completion state', '@req:Changes automatically save on navigation (Next/Previous)'],
  }, async ({
    page,
  }) => {
    // Create a real API scenario with exactly 10 traces
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'UI Last Trace Bug Test' })
      .withFacilitator()
      .withSMEs(1)
      .withTraces(10)
      .withRubric({ question: 'How helpful is this response?' })
      .inPhase(WorkshopPhase.ANNOTATION)
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const sme = scenario.users.sme[0];

    // Navigate to the app and login as SME
    await page.goto(`/?workshop=${workshopId}`);
    await scenario.loginAs(sme);

    // Wait for annotation interface to load
    await expect(page.getByText('Rate this Response')).toBeVisible({
      timeout: 20000,
    });

    // Annotate all 10 traces through the UI
    for (let i = 0; i < 10; i++) {
      // Wait for the progress indicator to show correct trace number
      await waitForAnnotationProgress(page, i + 1, 10);

      // Wait for the nav button to be disabled (proves form is reset with no
      // ratings) before clicking a rating. On the last trace the button is
      // rendered as the Complete button instead of Next.
      if (i > 0) {
        const navButton = i < 9
          ? page.getByTestId('next-trace-button')
          : page.getByTestId('complete-annotation-button');
        await expect(navButton).toBeDisabled({ timeout: 5000 });
      }

      // Navigation is debounced at 300ms to prevent duplicate saves; pace the
      // loop like a human so the next click is not swallowed by the debounce.
      await page.waitForTimeout(350);

      // Select a rating - click the Likert button for "Agree" (rating 4)
      // The Likert scale uses role="button" divs with the number displayed inside
      const agreeButton = page.locator('[role="button"]').filter({ hasText: /^4$/ }).first();
      await expect(agreeButton).toBeVisible({ timeout: 5000 });
      await agreeButton.click();

      // Click Next (or Complete for the last trace)
      if (i < 9) {
        const nextButton = page.getByTestId('next-trace-button');
        await expect(nextButton).toBeEnabled({ timeout: 5000 });
        await nextButton.click();
      } else {
        // Last trace - click Complete button (final save is awaited)
        const completeButton = page.getByTestId('complete-annotation-button');
        await expect(completeButton).toBeEnabled({ timeout: 5000 });
        await completeButton.click();
      }
    }

    // The terminal completion screen replaces the trace UI (#155)
    await expect(page.getByTestId('annotation-complete-screen')).toBeVisible({
      timeout: 15000,
    });
    await expect(page.getByText('All Annotations Complete!')).toBeVisible();

    // CRITICAL: Verify all 10 annotations were saved server-side.
    // Traces 1-9 save in the background, so poll until they settle.
    await expect
      .poll(
        async () => {
          const annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
          return new Set(annotations.map((a) => a.trace_id)).size;
        },
        {
          message: 'Expected annotations for all 10 unique traces to persist server-side',
          timeout: 15000,
        }
      )
      .toBe(10);

    // The 10th trace specifically must be persisted (the original bug lost it)
    const annotations = await getAnnotations(page, workshopId, sme.id, API_URL);
    const tenthTraceAnnotation = annotations.find(
      (a) => a.trace_id === scenario.traces[9].id
    );
    expect(
      tenthTraceAnnotation,
      'The 10th trace annotation was not saved when clicking Complete'
    ).toBeDefined();

    await scenario.cleanup();
  });
});
