/**
 * Helpers for docs media generation. Demo specs drive the app like e2e tests
 * but their artifacts (screenshots, .webm videos) are written into the docs
 * site's static directory, organized per spec:
 *
 *   docs/static/demos/<SPEC_NAME>/<name>.png
 *   docs/static/demos/<SPEC_NAME>/<name>.webm
 *
 * Embed in docs as /docs/demos/<SPEC_NAME>/<name>.webm (baseUrl included),
 * or via <SpecCoverage spec="..." requirement="..." video="..." />.
 */
import path from 'node:path';
import { mkdir } from 'node:fs/promises';
import type { Locator, Page } from '@playwright/test';

/**
 * A natural pause between actions so recordings read like a person using the
 * app, not a script blurring through it. Default is tuned for "reading a bit,
 * then acting"; pass a shorter value for small movements.
 */
export async function beat(page: Page, ms = 1200): Promise<void> {
  await page.waitForTimeout(ms);
}

/**
 * Type into a field at human speed (visible in recordings, unlike fill()).
 */
export async function humanType(locator: Locator, text: string, delayMs = 24): Promise<void> {
  await locator.click();
  await locator.pressSequentially(text, { delay: delayMs });
}

const OUT_ROOT = process.env.DEMO_OUT_DIR
  ? path.resolve(process.env.DEMO_OUT_DIR)
  : // Playwright runs with cwd = client/
    path.resolve(process.cwd(), '../docs/static/demos');

function demoDir(spec: string): string {
  return path.join(OUT_ROOT, spec);
}

export async function snap(page: Page, spec: string, name: string): Promise<void> {
  const dir = demoDir(spec);
  await mkdir(dir, { recursive: true });
  await page.screenshot({ path: path.join(dir, `${name}.png`) });
}

/**
 * Closes the page and copies its recording to the demos directory.
 * Call as the final step of a demo — nothing can run on the page after this.
 */
export async function saveDemoVideo(page: Page, spec: string, name: string): Promise<void> {
  const video = page.video();
  if (!video) return;
  const dir = demoDir(spec);
  await mkdir(dir, { recursive: true });
  await page.close();
  await video.saveAs(path.join(dir, `${name}.webm`));
}
