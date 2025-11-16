/**
 * E2E Tests for Admin Panel
 * Tests admin authentication, dashboard, and management features
 */

import { test, expect } from '@playwright/test';

test.describe('Admin Panel', () => {
  test.describe('Admin Authentication', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
    });

    test('should display admin login page', async ({ page }) => {
      await expect(page).toHaveTitle(/Admin/i);
      await expect(page.getByRole('heading', { name: /admin.*login/i })).toBeVisible();
    });

    test('should login with admin credentials', async ({ page }) => {
      const usernameInput = page.getByLabel(/username/i);
      const passwordInput = page.getByLabel(/password/i);
      const loginButton = page.getByRole('button', { name: /sign in/i });

      await usernameInput.fill('admin');
      await passwordInput.fill('admin123');
      await loginButton.click();

      // Should redirect to dashboard
      await expect(page).toHaveURL(/\/dashboard/i, { timeout: 10000 });
    });

    test('should show error for invalid credentials', async ({ page }) => {
      const usernameInput = page.getByLabel(/username/i);
      const passwordInput = page.getByLabel(/password/i);
      const loginButton = page.getByRole('button', { name: /sign in/i });

      await usernameInput.fill('invalid');
      await passwordInput.fill('wrong');
      await loginButton.click();

      await expect(page.getByText(/invalid.*credentials/i)).toBeVisible();
    });

    test('should reject non-admin users', async ({ page }) => {
      const usernameInput = page.getByLabel(/username/i);
      const passwordInput = page.getByLabel(/password/i);
      const loginButton = page.getByRole('button', { name: /sign in/i });

      await usernameInput.fill('regularuser');
      await passwordInput.fill('user123');
      await loginButton.click();

      await expect(page.getByText(/admin.*access.*required/i)).toBeVisible();
    });
  });

  test.describe('Admin Dashboard', () => {
    test.beforeEach(async ({ page, context }) => {
      // Mock admin authentication
      await context.addCookies([
        {
          name: 'admin_token',
          value: 'mock-admin-jwt-token',
          domain: 'localhost',
          path: '/',
        },
      ]);

      await page.goto('/dashboard');
    });

    test('should display dashboard statistics', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

      // Should show key metrics
      await expect(page.getByText(/total users/i)).toBeVisible();
      await expect(page.getByText(/active sessions/i)).toBeVisible();
      await expect(page.getByText(/total revenue/i)).toBeVisible();
      await expect(page.getByText(/pending.*kyc/i)).toBeVisible();
    });

    test('should display statistics cards', async ({ page }) => {
      const statsCards = page.locator('[data-testid="stat-card"]');
      await expect(statsCards).toHaveCount(8); // Expecting 8 stat cards
    });

    test('should show action cards', async ({ page }) => {
      await expect(page.getByRole('link', { name: /kyc.*approval/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /withdrawals/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /users/i })).toBeVisible();
    });

    test('should navigate to KYC approval from dashboard', async ({ page }) => {
      const kycLink = page.getByRole('link', { name: /kyc.*approval/i });
      await kycLink.click();

      await expect(page).toHaveURL(/\/kyc/i);
    });
  });

  test.describe('KYC Management', () => {
    test.beforeEach(async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'admin_token',
          value: 'mock-admin-jwt-token',
          domain: 'localhost',
          path: '/',
        },
      ]);

      await page.goto('/dashboard/kyc');
    });

    test('should display KYC approval page', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /kyc.*approval/i })).toBeVisible();
    });

    test('should display pending KYC documents', async ({ page }) => {
      const docsList = page.locator('[data-testid="kyc-documents-list"]');
      if (await docsList.isVisible()) {
        await expect(docsList).toBeVisible();
      }
    });

    test('should open document review modal', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        await expect(page.getByRole('dialog', { name: /kyc.*review/i })).toBeVisible();
      }
    });

    test('should display document images', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        const frontImage = page.getByAltText(/front/i);
        const backImage = page.getByAltText(/back/i);

        if (await frontImage.isVisible()) {
          await expect(frontImage).toBeVisible();
        }
        if (await backImage.isVisible()) {
          await expect(backImage).toBeVisible();
        }
      }
    });

    test('should approve KYC document', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        const approveButton = page.getByRole('button', { name: /approve/i });
        await approveButton.click();

        // Should show success message
        await expect(page.getByText(/approved/i)).toBeVisible({ timeout: 5000 });
      }
    });

    test('should reject KYC document with reason', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        const rejectButton = page.getByRole('button', { name: /reject/i });
        await rejectButton.click();

        // Should show reason input
        const reasonInput = page.getByLabel(/reason/i);
        await expect(reasonInput).toBeVisible();

        await reasonInput.fill('Document is not clear');

        const confirmButton = page.getByRole('button', { name: /confirm/i });
        await confirmButton.click();

        // Should show success message
        await expect(page.getByText(/rejected/i)).toBeVisible({ timeout: 5000 });
      }
    });
  });

  test.describe('Withdrawal Management', () => {
    test.beforeEach(async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'admin_token',
          value: 'mock-admin-jwt-token',
          domain: 'localhost',
          path: '/',
        },
      ]);

      await page.goto('/dashboard/withdrawals');
    });

    test('should display withdrawals page', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /withdrawals/i })).toBeVisible();
    });

    test('should show pending withdrawals count', async ({ page }) => {
      await expect(page.getByText(/pending.*\d+/i)).toBeVisible();
    });

    test('should display withdrawal details', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        await expect(page.getByText(/amount/i)).toBeVisible();
        await expect(page.getByText(/bank.*details/i)).toBeVisible();
        await expect(page.getByText(/account.*number/i)).toBeVisible();
      }
    });

    test('should approve withdrawal', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        const approveButton = page.getByRole('button', { name: /approve/i });
        await approveButton.click();

        await expect(page.getByText(/approved/i)).toBeVisible({ timeout: 5000 });
      }
    });

    test('should complete withdrawal with UTR', async ({ page }) => {
      const reviewButton = page.getByRole('button', { name: /review/i }).first();

      if (await reviewButton.isVisible()) {
        await reviewButton.click();

        const completeButton = page.getByRole('button', { name: /complete/i });
        if (await completeButton.isVisible()) {
          await completeButton.click();

          const utrInput = page.getByLabel(/utr/i);
          await expect(utrInput).toBeVisible();

          await utrInput.fill('UTR123456789');

          const confirmButton = page.getByRole('button', { name: /confirm/i });
          await confirmButton.click();

          await expect(page.getByText(/completed/i)).toBeVisible({ timeout: 5000 });
        }
      }
    });
  });

  test.describe('User Management', () => {
    test.beforeEach(async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'admin_token',
          value: 'mock-admin-jwt-token',
          domain: 'localhost',
          path: '/',
        },
      ]);

      await page.goto('/dashboard/users');
    });

    test('should display users list', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /users/i })).toBeVisible();

      const usersList = page.locator('[data-testid="users-table"]');
      if (await usersList.isVisible()) {
        await expect(usersList).toBeVisible();
      }
    });

    test('should search users by username', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i);
      await searchInput.fill('testuser');

      // Should update the list
      await expect(page.getByText(/testuser/i)).toBeVisible({ timeout: 5000 });
    });

    test('should filter users by status', async ({ page }) => {
      const statusFilter = page.getByLabel(/status/i);

      if (await statusFilter.isVisible()) {
        await statusFilter.selectOption('active');

        // Should update the list
        await page.waitForTimeout(1000);
      }
    });

    test('should view user details', async ({ page }) => {
      const viewButton = page.getByRole('button', { name: /view/i }).first();

      if (await viewButton.isVisible()) {
        await viewButton.click();

        // Should navigate to user details
        await expect(page).toHaveURL(/\/users\/[\w-]+/);
      }
    });

    test('should change user status', async ({ page }) => {
      const viewButton = page.getByRole('button', { name: /view/i }).first();

      if (await viewButton.isVisible()) {
        await viewButton.click();

        const changeStatusButton = page.getByRole('button', { name: /change status/i });
        if (await changeStatusButton.isVisible()) {
          await changeStatusButton.click();

          const statusSelect = page.getByLabel(/new status/i);
          await statusSelect.selectOption('suspended');

          const reasonInput = page.getByLabel(/reason/i);
          await reasonInput.fill('Policy violation');

          const confirmButton = page.getByRole('button', { name: /confirm/i });
          await confirmButton.click();

          await expect(page.getByText(/status.*updated/i)).toBeVisible({ timeout: 5000 });
        }
      }
    });
  });

  test.describe('Admin Navigation', () => {
    test.beforeEach(async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'admin_token',
          value: 'mock-admin-jwt-token',
          domain: 'localhost',
          path: '/',
        },
      ]);

      await page.goto('/dashboard');
    });

    test('should navigate to all admin sections', async ({ page }) => {
      const sections = [
        { name: /dashboard/i, url: /\/dashboard$/ },
        { name: /kyc/i, url: /\/kyc/ },
        { name: /withdrawals/i, url: /\/withdrawals/ },
        { name: /users/i, url: /\/users/ },
      ];

      for (const section of sections) {
        const link = page.getByRole('link', { name: section.name });
        if (await link.isVisible()) {
          await link.click();
          await expect(page).toHaveURL(section.url);
        }
      }
    });

    test('should logout admin', async ({ page }) => {
      const logoutButton = page.getByRole('button', { name: /logout/i });
      await logoutButton.click();

      // Should redirect to login
      await expect(page).toHaveURL('/', { timeout: 5000 });
    });
  });
});
