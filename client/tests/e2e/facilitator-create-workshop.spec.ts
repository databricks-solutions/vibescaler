import { test, expect } from '@playwright/test';

const API_URL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000';

test('facilitator can create a workshop from provider session', {
  tag: ['@spec:AUTHENTICATION_SPEC', '@spec:DISCOVERY_TRACE_ASSIGNMENT_SPEC'],
}, async ({ page, request }) => {
  await page.goto('/');

  // Local/provider auth should land facilitators on workshop creation when no workshop is selected.
  await expect(page.getByText(/Welcome, Facilitator/i)).toBeVisible();

  // Fill required Use Case Description before creating
  await page.locator('#description').fill('E2E test workshop for facilitator login flow');

  // Create workshop (real POST /workshops through Vite proxy)
  await Promise.all([
    page.waitForResponse((resp) => resp.request().method() === 'POST' && resp.url().includes('/workshops') && resp.status() === 201),
    page.getByRole('button', { name: /Create Workshop/i }).click(),
  ]);

  await expect(page).toHaveURL(/\?workshop=[a-f0-9-]{36}/i);
  const workshopId = new URL(page.url()).searchParams.get('workshop');
  expect(workshopId, 'workshop id should be present in URL').toMatch(/^[a-f0-9-]{36}$/i);

  // Sanity-check the backend state via API (bypasses browser CORS)
  const workshopResp = await request.get(`${API_URL}/workshops/${workshopId}`);
  expect(workshopResp.ok(), 'created workshop should be retrievable from API').toBeTruthy();
});

