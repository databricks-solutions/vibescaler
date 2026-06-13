/**
 * Docs demo: an SME Reviewer annotating a trace against the rubric.
 *
 * Not part of the e2e suite — runs only under `just docs-demos` (PW_DEMOS=1)
 * and exists to generate docs media, not to assert behavior. Unlike e2e
 * actions, every step here is deliberately paced and visible: the recording
 * has to read like a person reviewing, deciding, and explaining. Writes:
 *   docs/static/demos/ANNOTATION_SPEC/annotation-interface.png
 *   docs/static/demos/ANNOTATION_SPEC/annotation-filled.png
 *   docs/static/demos/ANNOTATION_SPEC/annotation-submitted.png
 *   docs/static/demos/ANNOTATION_SPEC/annotation-flow.webm
 */
import { test } from '@playwright/test';
import { TestScenario } from '../lib';
import { DEFAULT_API_URL } from '../lib/data';
import { waitForAnnotationInterface } from '../lib/actions/annotation';
import { beginAnnotation } from '../lib/actions/workshop';
import { WorkshopPhase } from '../lib/types';
import { snap, saveDemoVideo, beat, humanType } from './lib/recorder';

const API_URL = process.env.E2E_API_URL ?? DEFAULT_API_URL;
const SPEC = 'ANNOTATION_SPEC';

test('annotation flow walkthrough', async ({ page }) => {
  test.setTimeout(120_000);

  const scenario = await TestScenario.create(page)
    .withWorkshop({ name: 'Quality Review Session' })
    .withFacilitator()
    .withSMEs(1)
    .withRubric({ question: 'Helpfulness: Rate how helpful the response is' })
    .inPhase(WorkshopPhase.INTAKE)
    .withRealApi()
    .build();

  const workshopId = scenario.workshop.id;

  const uploadResponse = await page.request.post(`${API_URL}/workshops/${workshopId}/traces`, {
    data: [
      {
        input:
          'We need to rotate the API credentials for our production ingestion service. Can we do that without taking the pipeline down?',
        output:
          'Yes — rotation is zero-downtime if you do it in two steps. First, generate a second credential from Settings → Service Credentials; both keys stay valid during the grace period. Point the ingestion service at the new key, confirm events are flowing, then revoke the old key. The grace period defaults to 24 hours, so avoid revoking early if any batch jobs still reference the old credential.',
        context: { spans: [] },
      },
    ],
  });
  if (!uploadResponse.ok()) {
    throw new Error(`Trace upload failed: ${uploadResponse.status()}`);
  }

  await beginAnnotation(page, workshopId, API_URL);

  await page.goto(`/?workshop=${workshopId}`);
  await scenario.loginAs(scenario.users.sme[0]);
  await waitForAnnotationInterface(page);

  // Read the trace before doing anything.
  await beat(page, 2500);
  await snap(page, SPEC, 'annotation-interface');

  // Consider the scale, then commit to a rating — visibly.
  const rating = (value: number) =>
    page.locator('[role="button"]').filter({ hasText: new RegExp(`^${value}$`) }).first();
  await rating(3).hover();
  await beat(page, 900);
  await rating(4).hover();
  await beat(page, 700);
  await rating(4).click();
  await beat(page, 1400);

  // Explain the rating — typed at human speed, since this rationale is what
  // the judge aligns on.
  const comment = page.locator('#comment').or(page.locator('textarea[name="comment"]')).first();
  await humanType(
    comment,
    'Helpful and actionable: it confirms zero-downtime rotation, gives the two-step order, and flags the grace-period pitfall. It could be stronger with a link to the batch-job credential settings.'
  );
  await beat(page, 1500);
  await snap(page, SPEC, 'annotation-filled');

  // Submit and let the completion state breathe.
  const submit = page
    .getByTestId('next-trace-button')
    .or(page.getByTestId('complete-annotation-button'))
    .first();
  await submit.click();
  await beat(page, 2200);
  await snap(page, SPEC, 'annotation-submitted');

  await scenario.cleanup();
  await saveDemoVideo(page, SPEC, 'annotation-flow');
});
