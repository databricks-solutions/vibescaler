import { test, expect } from '@playwright/test';

test('provider session routes into the selected workshop without reload', async ({ page }) => {
  // Valid UUID for WorkshopContext validation
  const VALID_UUID = '12345678-1234-1234-1234-123456789012';

  const TEST_USER = {
    id: 'test-user-123',
    email: 'test@example.com',
    name: 'Test User',
    role: 'participant',
    workshop_id: VALID_UUID,
    status: 'active',
    created_at: new Date().toISOString()
  };

  const TEST_WORKSHOP = {
    id: VALID_UUID,
    name: 'Test Workshop',
    status: 'active',
    completed_phases: [],
    discovery_started: true,
    annotation_started: false
  };

  // MOCK ENDPOINTS

  // 1. Current session mock
  await page.route('**/api/auth/session', async route => {
    if (route.request().resourceType() === 'fetch') {
      await route.fulfill({
        json: {
          user: TEST_USER,
          permissions: { can_view_discovery: true, can_annotate: true },
          provider: 'e2e_mock',
          provider_role: 'CAN_USE',
        },
      });
    } else {
      await route.fallback();
    }
  });

  // 2. User Validation Mock
  await page.route((url) => url.toString().includes(`/users/${TEST_USER.id}`), async route => {
    if (route.request().resourceType() === 'fetch') {
      await route.fulfill({ json: TEST_USER });
    } else {
      await route.fallback();
    }
  });

  // 3. Workshop Data Mock
  await page.route((url) => url.toString().includes(`/workshops/${TEST_WORKSHOP.id}`), async route => {
    if (route.request().resourceType() === 'fetch') {
      await route.fulfill({ json: TEST_WORKSHOP });
    } else {
      await route.fallback();
    }
  });

  // 4. Rubric Mock
  await page.route('**/rubric', async route => {
    if (route.request().resourceType() === 'fetch') {
      await route.fulfill({ json: { criteria: [] } });
    } else {
      await route.fallback();
    }
  });

  await page.goto(`http://localhost:3000/workshop/${VALID_UUID}`);

  // Verify routing happens immediately (no reload needed)
  await expect(page.getByText('Test Workshop')).toBeVisible({ timeout: 5000 });
});

