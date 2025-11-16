/**
 * Authentication helpers for E2E tests
 */

import { Page, BrowserContext } from '@playwright/test';

export interface TestUser {
  phone: string;
  otp: string;
  username?: string;
}

export const TEST_USERS = {
  regularUser: {
    phone: '+919876543210',
    otp: '123456',
    username: 'testuser',
  },
  adminUser: {
    phone: '+919876543211',
    otp: '123456',
    username: 'admin',
  },
  premiumUser: {
    phone: '+919876543212',
    otp: '123456',
    username: 'premiumuser',
  },
};

/**
 * Login user via OTP flow
 */
export async function loginUser(page: Page, user: TestUser) {
  await page.goto('/');

  // Fill phone number
  const phoneInput = page.getByLabel(/phone/i);
  await phoneInput.fill(user.phone);

  // Click send OTP
  const sendOTPButton = page.getByRole('button', { name: /send otp/i });
  await sendOTPButton.click();

  // Wait for OTP input
  const otpInput = page.getByLabel(/otp/i);
  await otpInput.waitFor({ state: 'visible', timeout: 5000 });

  // Fill OTP
  await otpInput.fill(user.otp);

  // Click verify
  const verifyButton = page.getByRole('button', { name: /verify/i });
  await verifyButton.click();

  // Wait for redirect to dashboard
  await page.waitForURL(/\/dashboard/i, { timeout: 10000 });
}

/**
 * Set mock auth token in cookies
 */
export async function setMockAuthToken(
  context: BrowserContext,
  token: string = 'mock-jwt-token'
) {
  await context.addCookies([
    {
      name: 'auth_token',
      value: token,
      domain: 'localhost',
      path: '/',
    },
  ]);
}

/**
 * Set mock admin token in cookies
 */
export async function setMockAdminToken(
  context: BrowserContext,
  token: string = 'mock-admin-jwt-token'
) {
  await context.addCookies([
    {
      name: 'admin_token',
      value: token,
      domain: 'localhost',
      path: '/',
    },
  ]);
}

/**
 * Logout user
 */
export async function logoutUser(page: Page) {
  const logoutButton = page.getByRole('button', { name: /logout/i });
  await logoutButton.click();
  await page.waitForURL('/', { timeout: 5000 });
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const cookies = await page.context().cookies();
  return cookies.some((cookie) => cookie.name === 'auth_token');
}
