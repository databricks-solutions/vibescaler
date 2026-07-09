/**
 * E2E Test: Discovery feedback full participant flow
 *
 * Tests the complete participant journey through the UI:
 * submit feedback → answer 3 follow-up questions → completion state.
 * Also tests facilitator view of participant feedback details.
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib/scenario-builder';
import { WorkshopPhase } from '../lib/types';

declare const process: { env: Record<string, string | undefined> };

const API_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';

test.describe('Discovery feedback full participant flow', () => {

  test('participant completes feedback + 3 follow-up questions for a trace', {
    tag: [
      '@spec:DISCOVERY_SPEC',
      '@req:Progressive disclosure (one question at a time)',
      '@e2e-real',
    ],
  }, async ({ browser }) => {
    // Setup: TestScenario with real API, 1 trace, demo model
    const scenario = await TestScenario.create(browser)
      .withWorkshop({ name: 'Full Flow Feedback Test' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(1)
      .inPhase(WorkshopPhase.DISCOVERY)
      .withRealApi()
      .build();

    // Start discovery
    await scenario.loginAs(scenario.facilitator);
    await scenario.beginDiscovery(1);

    const participant = scenario.users.participant[0];

    // 1. Login as participant
    const participantPage = await scenario.newPageAs(participant);

    // 2. Submit feedback (select GOOD, type comment, click Submit)
    await participantPage.getByText('Good').click();

    const commentInput = participantPage.getByPlaceholder(
      'What specifically about this response influenced your rating?'
    );
    await commentInput.fill('The response is thorough and well-structured.');

    await participantPage.getByRole('button', { name: /Submit Feedback/i }).click();

    // 3. Wait for Q1 to appear (loading spinner may flash briefly in demo mode)
    // In demo mode the question generates almost instantly, so wait for the question directly
    await expect(
      participantPage.getByText('Question 1')
    ).toBeVisible({ timeout: 30000 });

    // 4. Answer Q1, submit
    const answerInput = participantPage.getByPlaceholder('Type your answer...');
    await answerInput.fill('The reasoning was clear and well-supported.');

    await participantPage.getByRole('button', { name: /Submit Answer/i }).click();

    // 5. Wait for Q2 to appear
    await expect(
      participantPage.getByText('Question 2')
    ).toBeVisible({ timeout: 15000 });

    // 6. Answer Q2, submit
    await participantPage.getByPlaceholder('Type your answer...').fill(
      'No significant gaps in the analysis.'
    );
    await participantPage.getByRole('button', { name: /Submit Answer/i }).click();

    // 7. Wait for Q3 to appear
    await expect(
      participantPage.getByText('Question 3')
    ).toBeVisible({ timeout: 15000 });

    // 8. Answer Q3, submit
    await participantPage.getByPlaceholder('Type your answer...').fill(
      'Overall the response quality is high.'
    );
    await participantPage.getByRole('button', { name: /Submit Answer/i }).click();

    // 9. Verify completion state
    await expect(
      participantPage.getByText('Feedback complete for this trace')
    ).toBeVisible({ timeout: 15000 });

    // 10. Reload page → verify state persists
    await participantPage.reload();

    await expect(
      participantPage.getByText('Feedback complete for this trace')
    ).toBeVisible({ timeout: 15000 });

    // Previous Q&A pairs should still be visible
    await expect(
      participantPage.getByText('The reasoning was clear and well-supported.')
    ).toBeVisible();

    await scenario.cleanup();
  });

  test('facilitator sees participant feedback details in dashboard', {
    tag: [
      '@spec:DISCOVERY_SPEC',
      '@req:Facilitator can view participant feedback details (label, comment, follow-up Q&A)',
      '@e2e-real',
    ],
  }, async ({ browser }) => {
    // Setup: TestScenario, submit feedback via API for participant
    const scenario = await TestScenario.create(browser)
      .withWorkshop({ name: 'Facilitator View Test' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(1)
      .inPhase(WorkshopPhase.DISCOVERY)
      .withRealApi()
      .build();

    await scenario.loginAs(scenario.facilitator);
    await scenario.beginDiscovery(1);

    const participant = scenario.users.participant[0];
    const traceId = scenario.traces[0].id;
    const workshopId = scenario.workshop.id;

    // Submit feedback + Q&A via API
    await scenario.page.request.post(
      `${API_URL}/workshops/${workshopId}/discovery-feedback`,
      {
        data: {
          trace_id: traceId,
          user_id: participant.id,
          feedback_label: 'good',
          comment: 'Excellent response quality.',
        },
      },
    );

    for (let q = 1; q <= 3; q++) {
      await scenario.page.request.post(
        `${API_URL}/workshops/${workshopId}/submit-followup-answer`,
        {
          data: {
            trace_id: traceId,
            user_id: participant.id,
            question: `Follow-up question ${q}?`,
            answer: `Detailed answer ${q}.`,
          },
        },
      );
    }

    // AUDIT (2026-06): this block previously hid its assertions behind an
    // `if (await feedbackTab.isVisible())` guard keyed to a "Feedback Detail"
    // dashboard tab that no longer exists, so the test passed vacuously.
    // The facilitator now sees participant feedback directly on the trace
    // cards in FacilitatorDiscoveryWorkspace — assert that unconditionally.

    // 1. Reload so the workspace picks up the feedback submitted above.
    //    Reloading lands on the workshop selection screen — re-enter the workshop.
    await scenario.page.reload();
    await scenario.page.getByTestId(`workshop-card-${workshopId}`).click();

    // 2. Feedback comment is visible on the trace card
    await expect(
      scenario.page.getByText('Excellent response quality.')
    ).toBeVisible({ timeout: 15000 });

    // 3. Follow-up Q&A is collapsed on the card — expand and verify content
    const qnaToggle = scenario.page.getByText(/3 follow-up/i).first();
    await expect(qnaToggle).toBeVisible({ timeout: 10000 });
    await qnaToggle.click();
    await expect(
      scenario.page.getByText('Follow-up question 1?')
    ).toBeVisible({ timeout: 10000 });

    await scenario.cleanup();
  });
});
