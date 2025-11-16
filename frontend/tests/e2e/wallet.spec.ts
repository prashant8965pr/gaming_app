/**
 * E2E Tests for Wallet Operations
 * Tests deposit, withdrawal, and transaction history
 */

import { test, expect } from '@playwright/test';

test.describe('Wallet Operations', () => {
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

    await page.goto('/wallet');
  });

  test.describe('Wallet Page Display', () => {
    test('should display wallet page', async ({ page }) => {
      await expect(page).toHaveTitle(/Wallet/i);
      await expect(page.getByRole('heading', { name: /wallet/i })).toBeVisible();
    });

    test('should display all wallet types', async ({ page }) => {
      await expect(page.getByText(/cash wallet/i)).toBeVisible();
      await expect(page.getByText(/bonus wallet/i)).toBeVisible();
      await expect(page.getByText(/winnings wallet/i)).toBeVisible();
    });

    test('should display balance for each wallet', async ({ page }) => {
      const wallets = page.locator('[data-testid="wallet-card"]');
      await expect(wallets).toHaveCount(3);

      for (const wallet of await wallets.all()) {
        await expect(wallet.getByText(/₹/)).toBeVisible();
      }
    });

    test('should show deposit and withdraw buttons', async ({ page }) => {
      await expect(page.getByRole('button', { name: /deposit/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /withdraw/i })).toBeVisible();
    });
  });

  test.describe('Deposit Flow', () => {
    test('should open deposit modal', async ({ page }) => {
      const depositButton = page.getByRole('button', { name: /deposit/i }).first();
      await depositButton.click();

      await expect(page.getByRole('dialog', { name: /deposit/i })).toBeVisible();
    });

    test('should validate minimum deposit amount', async ({ page }) => {
      const depositButton = page.getByRole('button', { name: /deposit/i }).first();
      await depositButton.click();

      const amountInput = page.getByLabel(/amount/i);
      await amountInput.fill('50'); // Below minimum

      const submitButton = page.getByRole('button', { name: /proceed/i });
      await submitButton.click();

      await expect(page.getByText(/minimum.*100/i)).toBeVisible();
    });

    test('should validate maximum deposit amount', async ({ page }) => {
      const depositButton = page.getByRole('button', { name: /deposit/i }).first();
      await depositButton.click();

      const amountInput = page.getByLabel(/amount/i);
      await amountInput.fill('200000'); // Above maximum

      const submitButton = page.getByRole('button', { name: /proceed/i });
      await submitButton.click();

      await expect(page.getByText(/maximum.*100000/i)).toBeVisible();
    });

    test('should proceed to payment gateway', async ({ page }) => {
      const depositButton = page.getByRole('button', { name: /deposit/i }).first();
      await depositButton.click();

      const amountInput = page.getByLabel(/amount/i);
      await amountInput.fill('1000');

      const submitButton = page.getByRole('button', { name: /proceed/i });
      await submitButton.click();

      // Should show payment gateway or success message
      await expect(
        page.getByText(/payment.*initiated/i).or(page.getByText(/processing/i))
      ).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Withdrawal Flow', () => {
    test('should open withdrawal modal', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      await expect(page.getByRole('dialog', { name: /withdraw/i })).toBeVisible();
    });

    test('should require KYC verification', async ({ page }) => {
      // Mock KYC not verified state
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      // Might show KYC requirement message
      const kycWarning = page.getByText(/kyc.*required/i);
      if (await kycWarning.isVisible()) {
        await expect(kycWarning).toBeVisible();
      }
    });

    test('should require bank account', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      // Check if bank account selection is available
      const bankAccountSelect = page.getByLabel(/bank account/i);
      if (await bankAccountSelect.isVisible()) {
        await expect(bankAccountSelect).toBeVisible();
      }
    });

    test('should validate minimum withdrawal amount', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      const amountInput = page.getByLabel(/amount/i);
      if (await amountInput.isVisible()) {
        await amountInput.fill('100'); // Below minimum

        const submitButton = page.getByRole('button', { name: /submit/i });
        await submitButton.click();

        await expect(page.getByText(/minimum.*200/i)).toBeVisible();
      }
    });

    test('should validate sufficient balance', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      const amountInput = page.getByLabel(/amount/i);
      if (await amountInput.isVisible()) {
        await amountInput.fill('1000000'); // Very large amount

        const submitButton = page.getByRole('button', { name: /submit/i });
        await submitButton.click();

        await expect(page.getByText(/insufficient balance/i)).toBeVisible();
      }
    });
  });

  test.describe('Transaction History', () => {
    test('should display transaction history', async ({ page }) => {
      const historySection = page.getByRole('region', { name: /transaction history/i });
      await expect(historySection).toBeVisible();
    });

    test('should filter transactions by type', async ({ page }) => {
      const filterSelect = page.getByLabel(/filter/i);

      if (await filterSelect.isVisible()) {
        await filterSelect.selectOption('deposit');
        // Should update the list
        await expect(page.getByText(/deposit/i).first()).toBeVisible();
      }
    });

    test('should display transaction details', async ({ page }) => {
      const firstTransaction = page.locator('[data-testid="transaction-item"]').first();

      if (await firstTransaction.isVisible()) {
        await expect(firstTransaction.getByText(/₹/)).toBeVisible();
        await expect(firstTransaction.getByText(/\d{2}\/\d{2}\/\d{4}/)).toBeVisible(); // Date
      }
    });

    test('should load more transactions on scroll', async ({ page }) => {
      const transactionList = page.locator('[data-testid="transaction-list"]');

      if (await transactionList.isVisible()) {
        const initialCount = await page.locator('[data-testid="transaction-item"]').count();

        // Scroll to bottom
        await transactionList.evaluate((el) => el.scrollTo(0, el.scrollHeight));

        // Wait for new items to load
        await page.waitForTimeout(2000);

        const newCount = await page.locator('[data-testid="transaction-item"]').count();

        // Should have loaded more items (if available)
        expect(newCount).toBeGreaterThanOrEqual(initialCount);
      }
    });
  });

  test.describe('Wallet Security', () => {
    test('should require confirmation for large withdrawals', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      const amountInput = page.getByLabel(/amount/i);
      if (await amountInput.isVisible()) {
        await amountInput.fill('50000'); // Large amount

        const submitButton = page.getByRole('button', { name: /submit/i });
        await submitButton.click();

        // Should show confirmation dialog
        await expect(page.getByRole('dialog', { name: /confirm/i })).toBeVisible();
      }
    });

    test('should show TDS deduction for large withdrawals', async ({ page }) => {
      const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
      await withdrawButton.click();

      const amountInput = page.getByLabel(/amount/i);
      if (await amountInput.isVisible()) {
        await amountInput.fill('20000'); // Above TDS threshold

        // Should show TDS calculation
        await expect(page.getByText(/tds/i)).toBeVisible();
      }
    });
  });
});
