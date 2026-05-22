/**
 * E2E tests for Authentication flow
 *
 * These tests verify success criteria from AUTHENTICATION_SPEC.md:
 * - Slow network: Loading indicator shown until ready
 * - Missing provider identity: authentication-required state shown
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';

test.describe('Authentication Flow', { tag: ['@spec:AUTHENTICATION_SPEC'] }, () => {

  test('loading indicator shown while current session loads on slow network', { tag: "@req:Slow network: Loading indicator shown until ready" },  async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Slow Network Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .inPhase('intake')
      .build();

    await page.route('**/api/auth/session', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: scenario.facilitator,
          permissions: {
            can_view_discovery: true,
            can_create_rubric: true,
            can_manage_workshop: true,
            can_manage_project: true,
          },
          provider: 'e2e_mock',
          provider_role: 'CAN_MANAGE',
        }),
      });
    });

    await page.goto('/');

    const loadingIndicator = page.locator('[aria-busy="true"]').or(page.locator('.animate-spin'));
    await expect(loadingIndicator.first()).toBeVisible({ timeout: 3000 });

    await scenario.cleanup();
  });

  test('missing provider identity shows authentication required', async ({ page }) => {
    await TestScenario.create(page)
      .withWorkshop({ name: 'Error Recovery Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .inPhase('intake')
      .build();

    await page.route('**/api/auth/session', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Missing provider identity' }),
      });
    });

    await page.goto('/');
    await expect(page.getByText('Authentication required')).toBeVisible({ timeout: 10000 });
  });
});
