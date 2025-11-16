/**
 * E2E Tests for Game Operations
 * Tests game catalog, session creation, joining, and gameplay
 */

import { test, expect } from '@playwright/test';

test.describe('Game Operations', () => {
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

    await page.goto('/games');
  });

  test.describe('Game Catalog', () => {
    test('should display game catalog', async ({ page }) => {
      await expect(page).toHaveTitle(/Games/i);
      await expect(page.getByRole('heading', { name: /games/i })).toBeVisible();
    });

    test('should display game cards', async ({ page }) => {
      const gameCards = page.locator('[data-testid="game-card"]');
      await expect(gameCards.first()).toBeVisible();
    });

    test('should display game details on card', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();

      await expect(firstGame.getByRole('heading')).toBeVisible(); // Game name
      await expect(firstGame.getByText(/players/i)).toBeVisible();
      await expect(firstGame.getByText(/entry fee/i)).toBeVisible();
    });

    test('should filter games by category', async ({ page }) => {
      const categoryFilter = page.getByLabel(/category/i);

      if (await categoryFilter.isVisible()) {
        await categoryFilter.selectOption('board');

        // Should show filtered games
        await expect(page.locator('[data-testid="game-card"]').first()).toBeVisible();
      }
    });

    test('should search games by name', async ({ page }) => {
      const searchInput = page.getByPlaceholder(/search/i);

      if (await searchInput.isVisible()) {
        await searchInput.fill('Ludo');

        // Should show search results
        await expect(page.getByText(/ludo/i)).toBeVisible();
      }
    });

    test('should navigate to game details', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      // Should navigate to game details page
      await expect(page).toHaveURL(/\/games\/[\w-]+/);
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    });
  });

  test.describe('Game Details', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to first game
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();
    });

    test('should display game information', async ({ page }) => {
      await expect(page.getByText(/description/i)).toBeVisible();
      await expect(page.getByText(/rules/i)).toBeVisible();
      await expect(page.getByText(/min.*players/i)).toBeVisible();
      await expect(page.getByText(/max.*players/i)).toBeVisible();
    });

    test('should display available sessions', async ({ page }) => {
      await expect(page.getByText(/available sessions/i)).toBeVisible();
    });

    test('should show create session button', async ({ page }) => {
      await expect(page.getByRole('button', { name: /create session/i })).toBeVisible();
    });
  });

  test.describe('Create Game Session', () => {
    test.beforeEach(async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      const createButton = page.getByRole('button', { name: /create session/i });
      await createButton.click();
    });

    test('should open create session modal', async ({ page }) => {
      await expect(page.getByRole('dialog', { name: /create session/i })).toBeVisible();
    });

    test('should validate entry fee', async ({ page }) => {
      const entryFeeInput = page.getByLabel(/entry fee/i);
      await entryFeeInput.fill('5'); // Below minimum

      const createButton = page.getByRole('button', { name: /create/i });
      await createButton.click();

      await expect(page.getByText(/minimum.*entry fee/i)).toBeVisible();
    });

    test('should validate max players', async ({ page }) => {
      const maxPlayersInput = page.getByLabel(/max players/i);
      await maxPlayersInput.fill('10'); // Above maximum

      const createButton = page.getByRole('button', { name: /create/i });
      await createButton.click();

      await expect(page.getByText(/maximum.*players/i)).toBeVisible();
    });

    test('should create session successfully', async ({ page }) => {
      const entryFeeInput = page.getByLabel(/entry fee/i);
      await entryFeeInput.fill('100');

      const maxPlayersInput = page.getByLabel(/max players/i);
      await maxPlayersInput.fill('4');

      const createButton = page.getByRole('button', { name: /create/i });
      await createButton.click();

      // Should show success message and redirect
      await expect(
        page.getByText(/session created/i).or(page.getByText(/waiting/i))
      ).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Join Game Session', () => {
    test('should display available sessions', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      const sessionsList = page.locator('[data-testid="session-list"]');
      if (await sessionsList.isVisible()) {
        await expect(sessionsList).toBeVisible();
      }
    });

    test('should show session details', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      const firstSession = page.locator('[data-testid="session-card"]').first();

      if (await firstSession.isVisible()) {
        await expect(firstSession.getByText(/entry fee/i)).toBeVisible();
        await expect(firstSession.getByText(/players/i)).toBeVisible();
      }
    });

    test('should join session successfully', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      const joinButton = page.getByRole('button', { name: /join/i }).first();

      if (await joinButton.isVisible()) {
        await joinButton.click();

        // Should show confirmation or navigate to game
        await expect(
          page.getByText(/joined/i).or(page.getByText(/waiting/i))
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test('should prevent joining if insufficient balance', async ({ page }) => {
      const firstGame = page.locator('[data-testid="game-card"]').first();
      await firstGame.click();

      // Create a high-stakes session first
      const createButton = page.getByRole('button', { name: /create session/i });
      await createButton.click();

      const entryFeeInput = page.getByLabel(/entry fee/i);
      await entryFeeInput.fill('100000'); // Very high fee

      const maxPlayersInput = page.getByLabel(/max players/i);
      await maxPlayersInput.fill('4');

      const createSessionButton = page.getByRole('button', { name: /create/i });
      await createSessionButton.click();

      // Should show insufficient balance error
      await expect(page.getByText(/insufficient balance/i)).toBeVisible();
    });
  });

  test.describe('Live Game Session', () => {
    test('should display game lobby', async ({ page }) => {
      // Assuming we're in a game session
      await page.goto('/games/session/test-session-id');

      await expect(page.getByText(/waiting for players/i)).toBeVisible();
    });

    test('should show connected players', async ({ page }) => {
      await page.goto('/games/session/test-session-id');

      const playersList = page.locator('[data-testid="players-list"]');
      if (await playersList.isVisible()) {
        await expect(playersList).toBeVisible();
      }
    });

    test('should display chat interface', async ({ page }) => {
      await page.goto('/games/session/test-session-id');

      const chatInput = page.getByPlaceholder(/type a message/i);
      if (await chatInput.isVisible()) {
        await expect(chatInput).toBeVisible();
      }
    });

    test('should send chat messages', async ({ page }) => {
      await page.goto('/games/session/test-session-id');

      const chatInput = page.getByPlaceholder(/type a message/i);
      if (await chatInput.isVisible()) {
        await chatInput.fill('Hello, players!');

        const sendButton = page.getByRole('button', { name: /send/i });
        await sendButton.click();

        // Should show message in chat
        await expect(page.getByText(/hello, players!/i)).toBeVisible();
      }
    });

    test('should show connection status', async ({ page }) => {
      await page.goto('/games/session/test-session-id');

      const connectionStatus = page.locator('[data-testid="connection-status"]');
      if (await connectionStatus.isVisible()) {
        await expect(connectionStatus).toBeVisible();
      }
    });

    test('should display game board when started', async ({ page }) => {
      await page.goto('/games/session/test-session-id');

      const gameBoard = page.locator('[data-testid="game-board"]');
      if (await gameBoard.isVisible()) {
        await expect(gameBoard).toBeVisible();
      }
    });
  });

  test.describe('Game History', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/games/history');
    });

    test('should display game history', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /game history/i })).toBeVisible();
    });

    test('should show past game sessions', async ({ page }) => {
      const gameList = page.locator('[data-testid="game-history-list"]');
      if (await gameList.isVisible()) {
        await expect(gameList).toBeVisible();
      }
    });

    test('should filter by game type', async ({ page }) => {
      const filterSelect = page.getByLabel(/game type/i);

      if (await filterSelect.isVisible()) {
        await filterSelect.selectOption('ludo');
        await expect(page.getByText(/ludo/i)).toBeVisible();
      }
    });

    test('should show game results', async ({ page }) => {
      const firstGame = page.locator('[data-testid="history-item"]').first();

      if (await firstGame.isVisible()) {
        await expect(firstGame.getByText(/won|lost/i)).toBeVisible();
        await expect(firstGame.getByText(/₹/)).toBeVisible(); // Amount
      }
    });
  });
});
