/**
 * Authentication actions
 *
 * Provides login/logout functionality for e2e tests.
 */

import { expect, type Page } from '@playwright/test';
import type { User } from '../types';
import { UserRole } from '../types';
import { DEFAULT_FACILITATOR } from '../data';

/**
 * Helper to select a workshop from the dropdown
 */
async function selectWorkshopFromDropdown(page: Page, workshopId: string): Promise<void> {
  // Wait for "Loading workshops..." to disappear
  const loadingText = page.getByText(/Loading workshops/i);
  await expect(loadingText).not.toBeVisible({ timeout: 5000 }).catch(() => {});

  // Find the combobox (Select trigger)
  const workshopSelect = page.locator('button[role="combobox"]').first();
  if (!await workshopSelect.isVisible().catch(() => false)) {
    // No dropdown visible - might be auto-submitted or different UI state
    return;
  }

  // Check if the workshop is already selected by looking at the trigger's data-state
  // and the displayed text. If it shows the workshop name, we might be done.
  // The Radix Select sets aria-expanded when open
  const triggerText = await workshopSelect.textContent();

  // Click to open the dropdown
  await workshopSelect.click();

  // Wait for dropdown content to appear
  await page.waitForSelector('[role="listbox"]', { timeout: 3000 }).catch(() => {});
  await page.waitForTimeout(200);

  // Radix Select stores the value in data-value attribute on the option element
  // Try the data-value selector first (most reliable)
  const dataValueSelector = `[role="option"][data-value="${workshopId}"]`;
  const workshopOption = page.locator(dataValueSelector);

  if (await workshopOption.isVisible({ timeout: 1000 }).catch(() => false)) {
    await workshopOption.click();
  } else {
    // If data-value selector didn't work, check if the listbox is empty or workshop not found
    const availableOptions = await page.locator('[role="option"]').all();

    if (availableOptions.length === 0) {
      // No options available - might be a timing issue or no workshops
      // Close the dropdown by clicking elsewhere and throw
      await page.keyboard.press('Escape');
      throw new Error(
        `No workshop options available in dropdown. Expected workshop: ${workshopId}`
      );
    }

    const optionValues = await Promise.all(
      availableOptions.map(async (opt) => {
        const value = await opt.getAttribute('data-value');
        const text = await opt.textContent();
        return `${value}: ${text}`;
      })
    );

    // Close dropdown before throwing
    await page.keyboard.press('Escape');

    console.error(
      `[selectWorkshopFromDropdown] Could not find workshop ${workshopId}. ` +
      `Trigger showed: "${triggerText}". Available options: ${optionValues.join(', ')}`
    );
    throw new Error(
      `Workshop ${workshopId} not found in dropdown. ` +
      `Available: ${optionValues.join(', ')}`
    );
  }
}

/**
 * Login as a specific user
 *
 * Handles both facilitator login (with password) and participant login (email only).
 *
 * For facilitators: clicks "Create New" if no workshop_id is provided (to create new workshop)
 * For participants/SMEs: selects the workshop from dropdown if workshop_id is provided
 */
export async function loginAs(page: Page, user: User): Promise<void> {
  // V2 (provider-resolved auth): there is no login page. Identity comes from
  // GET /api/auth/session (mocked per-scenario) plus the legacy workshop_user
  // localStorage key that pre-provider components still read.
  const serialized = JSON.stringify(user);
  await page.addInitScript((value) => {
    window.localStorage.setItem('workshop_user', value);
  }, serialized);

  const target = user.workshop_id ? `/workshop/${user.workshop_id}` : '/';
  await page.goto(target);

  // Wait for React to mount
  await page.waitForSelector('#root > *', { timeout: 10000 });
  await page.evaluate((value) => {
    window.localStorage.setItem('workshop_user', value);
  }, serialized).catch(() => {});
  await page.waitForLoadState('networkidle');

  // If a workshop landing with cards is shown, enter the user's workshop.
  if (user.workshop_id) {
    const workshopCard = page.locator(`[data-testid="workshop-card-${user.workshop_id}"]`);
    if (await workshopCard.isVisible({ timeout: 2000 }).catch(() => false)) {
      await workshopCard.click();
      await page.waitForURL(/\?workshop=/, { timeout: 10000 }).catch(() => {});
    }
  }
}

/**
 * Login as facilitator using default credentials
 *
 * This assumes the facilitator wants to create a new workshop.
 */
export async function loginAsFacilitator(page: Page): Promise<void> {
  await loginAs(page, {
    id: 'facilitator-default',
    email: DEFAULT_FACILITATOR.email,
    name: DEFAULT_FACILITATOR.name,
    role: UserRole.FACILITATOR,
    workshop_id: null,
  } as User);
}

/**
 * Logout the current user
 */
export async function logout(page: Page): Promise<void> {
  // Look for logout button or dropdown
  const logoutButton = page.getByRole('button', { name: /logout|sign out/i });
  if (await logoutButton.isVisible().catch(() => false)) {
    await logoutButton.click();
  } else {
    // Try user menu dropdown
    const userMenu = page.getByRole('button', { name: /user|account|profile/i });
    if (await userMenu.isVisible().catch(() => false)) {
      await userMenu.click();
      await page.getByRole('menuitem', { name: /logout|sign out/i }).click();
    } else {
      // Fallback: clear storage and navigate to root
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      await page.goto('/');
    }
  }

  // V2 has no login page; verify the session storage is cleared instead.
  await page.evaluate(() => {
    localStorage.removeItem('workshop_user');
  }).catch(() => {});
}

/**
 * Set mock user in localStorage (for bypassing login in certain tests)
 */
export async function setMockUser(page: Page, user: User): Promise<void> {
  await page.addInitScript((userData) => {
    localStorage.setItem('workshop_user', JSON.stringify(userData));
  }, user);
}

/**
 * Clear the current user session
 */
export async function clearSession(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('workshop_user');
    sessionStorage.clear();
  });
}
