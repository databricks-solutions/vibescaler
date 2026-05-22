/**
 * Authentication actions
 *
 * Provides provider-session switching helpers for e2e tests.
 */

import { expect, type Page } from '@playwright/test';
import type { User } from '../types';
import { UserRole } from '../types';
import { DEFAULT_BASE_URL } from '../data';

async function setCurrentUserCookie(page: Page, user: User): Promise<void> {
  const currentUrl = page.url();
  const origin = currentUrl && currentUrl !== 'about:blank'
    ? new URL(currentUrl).origin
    : DEFAULT_BASE_URL;
  const providerRole = user.role === UserRole.FACILITATOR ? 'CAN_MANAGE' : 'CAN_USE';

  await page.context().addCookies([
    {
      name: 'e2e_current_user_id',
      value: user.id,
      url: origin,
    },
    {
      name: 'e2e_current_user_email',
      value: user.email,
      url: origin,
    },
    {
      name: 'e2e_current_user_name',
      value: user.name,
      url: origin,
    },
    {
      name: 'e2e_current_provider_role',
      value: providerRole,
      url: origin,
    },
  ]);
}

/**
 * Switch the mocked provider session to a specific user.
 */
export async function loginAs(page: Page, user: User): Promise<void> {
  await setCurrentUserCookie(page, user);
  const targetUrl = user.workshop_id ? `/workshop/${user.workshop_id}` : '/';
  await page.goto(targetUrl);
  await page.waitForSelector('#root > *', { timeout: 10000 });
  await page.waitForLoadState('networkidle').catch(() => {});
  await expect(page.getByText('Authentication required')).not.toBeVisible({ timeout: 10000 });
}

/**
 * Switch to the default facilitator in mocked scenarios.
 */
export async function loginAsFacilitator(page: Page): Promise<void> {
  await page.goto('/');
  await page.waitForSelector('#root > *', { timeout: 10000 });
}

/**
 * Logout the current user
 */
export async function logout(page: Page): Promise<void> {
  await page.context().clearCookies();
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.goto('/');
}

/**
 * Set mock user in localStorage (for bypassing login in certain tests)
 */
export async function setMockUser(page: Page, user: User): Promise<void> {
  await setCurrentUserCookie(page, user);
}

/**
 * Clear the current user session
 */
export async function clearSession(page: Page): Promise<void> {
  await page.context().clearCookies();
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}
