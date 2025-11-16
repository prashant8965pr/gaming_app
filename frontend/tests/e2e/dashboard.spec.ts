/**
 * E2E Tests for Dashboard
 * Tests dashboard display, statistics, and navigation
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock authentication
    await context.addCookies([
      {
        name: 'auth_token',
        value: 'mock-jwt-token',
        domain: 'localhost',
        path: '/',
      },
    ]);

    await page.goto('/dashboard');
  });

  test('should display dashboard page', async ({ page }) => {
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should display wallet balances', async ({ page }) => {
    // Should show wallet cards
    await expect(page.getByText(/cash balance/i)).toBeVisible();
    await expect(page.getByText(/bonus balance/i)).toBeVisible();
    await expect(page.getByText(/winnings/i)).toBeVisible();

    // Should show balance amounts (check for currency symbol)
    await expect(page.getByText(/₹/)).toBeVisible();
  });

  test('should display user statistics', async ({ page }) => {
    await expect(page.getByText(/games played/i)).toBeVisible();
    await expect(page.getByText(/wins/i)).toBeVisible();
    await expect(page.getByText(/total winnings/i)).toBeVisible();
  });

  test('should navigate to wallet page', async ({ page }) => {
    const walletLink = page.getByRole('link', { name: /wallet/i });
    await walletLink.click();

    await expect(page).toHaveURL(/\/wallet/i);
  });

  test('should navigate to games page', async ({ page }) => {
    const gamesLink = page.getByRole('link', { name: /games/i });
    await gamesLink.click();

    await expect(page).toHaveURL(/\/games/i);
  });

  test('should display recent transactions', async ({ page }) => {
    const transactionsSection = page.getByRole('region', { name: /recent transactions/i });
    await expect(transactionsSection).toBeVisible();
  });

  test('should display active game sessions', async ({ page }) => {
    const sessionsSection = page.getByRole('region', { name: /active sessions/i });
    await expect(sessionsSection).toBeVisible();
  });

  test('should show KYC status', async ({ page }) => {
    await expect(page.getByText(/kyc status/i)).toBeVisible();
  });

  test('should navigate to KYC verification if not verified', async ({ page }) => {
    // Assuming KYC is not verified
    const kycButton = page.getByRole('button', { name: /verify kyc/i });

    if (await kycButton.isVisible()) {
      await kycButton.click();
      await expect(page).toHaveURL(/\/kyc/i);
    }
  });
});
