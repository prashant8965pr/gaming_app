/**
 * E2E Tests for Authentication Flow
 * Tests OTP-based authentication, login, and logout
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Gaming Platform/i);
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
  });

  test('should show phone input field', async ({ page }) => {
    const phoneInput = page.getByLabel(/phone/i);
    await expect(phoneInput).toBeVisible();
    await expect(phoneInput).toHaveAttribute('type', 'tel');
  });

  test('should validate phone number format', async ({ page }) => {
    const phoneInput = page.getByLabel(/phone/i);
    const submitButton = page.getByRole('button', { name: /send otp/i });

    // Try invalid phone number
    await phoneInput.fill('123');
    await submitButton.click();

    // Should show validation error
    await expect(page.getByText(/invalid phone/i)).toBeVisible();
  });

  test('should send OTP for valid phone number', async ({ page }) => {
    const phoneInput = page.getByLabel(/phone/i);
    const submitButton = page.getByRole('button', { name: /send otp/i });

    // Enter valid phone number
    await phoneInput.fill('+919876543210');
    await submitButton.click();

    // Should show OTP input
    await expect(page.getByLabel(/otp/i)).toBeVisible({ timeout: 5000 });

    // Should show success message
    await expect(page.getByText(/otp sent/i)).toBeVisible();
  });

  test('should verify OTP and login successfully', async ({ page }) => {
    const phoneInput = page.getByLabel(/phone/i);
    const sendOTPButton = page.getByRole('button', { name: /send otp/i });

    // Send OTP
    await phoneInput.fill('+919876543210');
    await sendOTPButton.click();

    // Wait for OTP input
    const otpInput = page.getByLabel(/otp/i);
    await expect(otpInput).toBeVisible({ timeout: 5000 });

    // Enter OTP (in test environment, we might need to mock this)
    await otpInput.fill('123456');

    const verifyButton = page.getByRole('button', { name: /verify/i });
    await verifyButton.click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/i, { timeout: 10000 });

    // Should show user greeting
    await expect(page.getByText(/welcome/i)).toBeVisible();
  });

  test('should show error for invalid OTP', async ({ page }) => {
    const phoneInput = page.getByLabel(/phone/i);
    const sendOTPButton = page.getByRole('button', { name: /send otp/i });

    // Send OTP
    await phoneInput.fill('+919876543210');
    await sendOTPButton.click();

    // Enter invalid OTP
    const otpInput = page.getByLabel(/otp/i);
    await expect(otpInput).toBeVisible({ timeout: 5000 });
    await otpInput.fill('000000');

    const verifyButton = page.getByRole('button', { name: /verify/i });
    await verifyButton.click();

    // Should show error message
    await expect(page.getByText(/invalid otp/i)).toBeVisible();
  });

  test('should logout successfully', async ({ page, context }) => {
    // Assuming user is already logged in (you might need to add login helper)
    // For this test, we'll mock the auth state
    await context.addCookies([
      {
        name: 'auth_token',
        value: 'mock-jwt-token',
        domain: 'localhost',
        path: '/',
      },
    ]);

    await page.goto('/dashboard');

    // Click logout button
    const logoutButton = page.getByRole('button', { name: /logout/i });
    await logoutButton.click();

    // Should redirect to login page
    await expect(page).toHaveURL('/', { timeout: 5000 });

    // Should show login form
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
  });

  test('should persist session across page reloads', async ({ page, context }) => {
    // Set auth token
    await context.addCookies([
      {
        name: 'auth_token',
        value: 'mock-jwt-token',
        domain: 'localhost',
        path: '/',
      },
    ]);

    await page.goto('/dashboard');

    // Reload page
    await page.reload();

    // Should still be on dashboard
    await expect(page).toHaveURL(/\/dashboard/i);
    await expect(page.getByText(/welcome/i)).toBeVisible();
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL('/', { timeout: 5000 });
  });
});
