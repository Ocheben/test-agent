import { test, expect } from '@playwright/test';

test('chat flow shows agent response', async ({ page }) => {
  await page.route('**/chat', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ answer: 'Agent response' }),
    });
  });

  await page.goto('/');
  await page.fill('input', 'Hello');
  await page.click('button');
  await expect(page.locator('text=Agent response')).toBeVisible();
});
