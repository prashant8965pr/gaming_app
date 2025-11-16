# Gaming Platform - Testing Guide

Comprehensive guide for testing the gaming platform.

**Last Updated:** November 16, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Test Infrastructure](#test-infrastructure)
3. [Backend Testing](#backend-testing)
4. [Frontend E2E Testing](#frontend-e2e-testing)
5. [Load Testing](#load-testing)
6. [CI/CD Testing](#cicd-testing)
7. [Test Coverage](#test-coverage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The gaming platform uses a comprehensive testing strategy:

- **Unit Tests** - Backend business logic (pytest)
- **Integration Tests** - API endpoints and database (pytest)
- **E2E Tests** - Complete user journeys (Playwright)
- **Load Tests** - Performance and scalability (Locust)
- **Security Tests** - Vulnerability scanning (Bandit, Safety)

### Test Philosophy

- **Test Coverage:** Aim for >80% code coverage
- **Test Pyramid:** More unit tests, fewer E2E tests
- **Fast Feedback:** Tests should run quickly
- **Reliability:** Tests should be deterministic
- **Isolation:** Tests should not depend on each other

---

## Test Infrastructure

### Directory Structure

```
gaming_app/
├── backend/
│   └── tests/
│       ├── conftest.py          # Test fixtures
│       ├── test_auth.py         # Auth tests
│       ├── test_users.py        # User tests
│       ├── test_wallet.py       # Wallet tests
│       ├── test_games.py        # Game tests
│       ├── test_kyc.py          # KYC tests
│       └── test_rewards.py      # Rewards tests
│
├── frontend/
│   ├── playwright.config.ts    # Playwright config
│   └── tests/
│       └── e2e/
│           ├── auth.spec.ts     # Auth E2E tests
│           ├── dashboard.spec.ts
│           ├── wallet.spec.ts
│           ├── games.spec.ts
│           └── helpers/
│               └── auth.ts      # Test helpers
│
├── frontend-admin/
│   └── tests/
│       └── e2e/
│           └── admin.spec.ts    # Admin E2E tests
│
└── load-tests/
    └── locustfile.py           # Load testing scenarios
```

### Test Dependencies

**Backend:**
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for async client)

**Frontend:**
- @playwright/test
- @testing-library/react (optional)

**Load Testing:**
- locust

---

## Backend Testing

### Running Backend Tests

#### All Tests

```bash
cd backend
pytest
```

#### With Coverage

```bash
pytest --cov --cov-report=html --cov-report=term-missing
```

#### Specific Test File

```bash
pytest tests/test_auth.py
```

#### Specific Test Function

```bash
pytest tests/test_auth.py::test_send_otp
```

#### With Verbose Output

```bash
pytest -v
```

#### Stop on First Failure

```bash
pytest -x
```

### Test Fixtures

Available fixtures in `conftest.py`:

```python
# Database
db_session              # Async database session
test_db_engine          # Test database engine

# HTTP Client
client                  # Test HTTP client

# Users
test_user               # Regular user
test_user_2             # Second user
admin_user              # Admin user

# Authentication
auth_token              # User auth token
admin_token             # Admin auth token
auth_headers            # Auth headers
admin_headers           # Admin auth headers

# Wallet
test_wallets            # User wallets

# Games
test_game               # Test game
test_game_session       # Test game session

# KYC
test_kyc_document       # Test KYC document

# Rewards
test_daily_bonus        # Test daily bonus
test_achievement        # Test achievement

# Mocks
mock_payment_gateway    # Mock payment service
mock_sms_service        # Mock SMS service
mock_email_service      # Mock email service
```

### Example Test

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_profile(client: AsyncClient, auth_headers: dict):
    """Test getting user profile"""
    response = await client.get(
        "/api/v1/users/profile",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "username" in data["data"]
```

### Writing Tests

#### 1. Unit Tests

Test individual functions/methods:

```python
def test_calculate_prize_distribution():
    """Test prize distribution calculation"""
    from utils.game_utils import calculate_prize_distribution

    result = calculate_prize_distribution(
        total_pool=1000,
        distribution={"1st": 70, "2nd": 20, "3rd": 10}
    )

    assert result["1st"] == 700
    assert result["2nd"] == 200
    assert result["3rd"] == 100
```

#### 2. API Tests

Test API endpoints:

```python
@pytest.mark.asyncio
async def test_create_game_session(
    client: AsyncClient,
    auth_headers: dict,
    test_game
):
    """Test creating a game session"""
    response = await client.post(
        "/api/v1/games/sessions",
        headers=auth_headers,
        json={
            "game_id": str(test_game.id),
            "entry_fee": 100,
            "max_players": 4,
            "is_private": False
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "session_code" in data["data"]
```

#### 3. Database Tests

Test database operations:

```python
@pytest.mark.asyncio
async def test_user_creation(db_session):
    """Test creating a user in database"""
    from models.user import User

    user = User(
        username="newuser",
        phone="+919876543210",
        is_phone_verified=True
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.username == "newuser"
```

### Test Coverage Report

View coverage report:

```bash
# Generate HTML report
pytest --cov --cov-report=html

# Open in browser
open htmlcov/index.html
```

---

## Frontend E2E Testing

### Setup Playwright

```bash
cd frontend

# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Install system dependencies (Linux)
npx playwright install-deps
```

### Running E2E Tests

#### All Tests

```bash
npx playwright test
```

#### Headed Mode (See Browser)

```bash
npx playwright test --headed
```

#### Debug Mode

```bash
npx playwright test --debug
```

#### Specific Test File

```bash
npx playwright test auth.spec.ts
```

#### Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

#### UI Mode (Interactive)

```bash
npx playwright test --ui
```

### Test Report

View test results:

```bash
npx playwright show-report
```

### Writing E2E Tests

#### Basic Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await page.getByLabel('Username').fill('testuser');
    await page.getByRole('button', { name: /submit/i }).click();

    await expect(page).toHaveURL('/dashboard');
  });
});
```

#### Using Test Helpers

```typescript
import { loginUser, TEST_USERS } from './helpers/auth';

test('should access dashboard after login', async ({ page }) => {
  await loginUser(page, TEST_USERS.regularUser);

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/welcome/i)).toBeVisible();
});
```

#### Testing Forms

```typescript
test('should submit form', async ({ page }) => {
  await page.goto('/deposit');

  // Fill form
  await page.getByLabel(/amount/i).fill('1000');
  await page.getByLabel(/payment method/i).selectOption('razorpay');

  // Submit
  await page.getByRole('button', { name: /submit/i }).click();

  // Verify
  await expect(page.getByText(/success/i)).toBeVisible();
});
```

#### Testing API Responses

```typescript
test('should load data from API', async ({ page }) => {
  // Wait for API response
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/v1/games/catalog')
  );

  await page.goto('/games');

  const response = await responsePromise;
  expect(response.status()).toBe(200);

  // Verify data is displayed
  await expect(page.getByTestId('game-card')).toBeVisible();
});
```

### Visual Testing

Take screenshots for visual regression:

```typescript
test('should match screenshot', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png');
});
```

---

## Load Testing

### Setup Locust

```bash
pip install locust
```

### Running Load Tests

#### Web UI Mode

```bash
cd load-tests
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089

#### Headless Mode

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

### Test Scenarios

#### Light Load

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 2m
```

#### Stress Test

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m
```

#### Spike Test

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 500 \
  --spawn-rate 50 \
  --run-time 2m
```

#### Soak Test (Endurance)

```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2h
```

### Metrics to Monitor

- **Response Time:** p50, p95, p99
- **Requests per Second (RPS)**
- **Failure Rate**
- **Concurrent Users**
- **CPU Usage**
- **Memory Usage**
- **Database Connections**

### Performance Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| API Response Time (p95) | <200ms | <500ms |
| Page Load Time | <2s | <3s |
| Concurrent Users | 1000+ | - |
| Throughput | 100+ RPS | - |
| Error Rate | <0.1% | <1% |

---

## CI/CD Testing

Tests run automatically on every push via GitHub Actions.

### CI Workflow

`.github/workflows/ci.yml` runs:

1. **Linting** - Code quality checks
2. **Unit Tests** - Backend tests with coverage
3. **Security Scanning** - Dependency vulnerabilities
4. **Docker Build** - Verify images build successfully

### Viewing CI Results

1. Go to GitHub repository
2. Click "Actions" tab
3. Select workflow run
4. View logs and test results

### Coverage Reports

Coverage reports are uploaded to Codecov:

```
https://codecov.io/gh/your-username/gaming_app
```

---

## Test Coverage

### Current Coverage

| Component | Coverage | Target |
|-----------|----------|--------|
| Backend API | ~70% | >80% |
| Business Logic | ~60% | >80% |
| Frontend Components | ~40% | >70% |
| E2E Flows | ~80% | >90% |

### Improving Coverage

1. **Identify Gaps**
   ```bash
   pytest --cov --cov-report=term-missing
   ```

2. **Write Missing Tests**
   - Focus on critical paths first
   - Test edge cases
   - Test error handling

3. **Review Coverage Reports**
   - Check HTML coverage report
   - Look for untested lines
   - Prioritize high-risk code

---

## Best Practices

### General

1. **Descriptive Names** - Test names should describe what they test
2. **One Assertion per Test** - Keep tests focused
3. **Independent Tests** - Tests should not depend on each other
4. **Fast Tests** - Keep unit tests under 100ms
5. **Mock External Services** - Don't rely on external APIs

### Backend

```python
# ❌ Bad
def test_stuff():
    user = create_user()
    assert user

# ✅ Good
@pytest.mark.asyncio
async def test_create_user_returns_user_with_id(db_session):
    """Test that creating a user returns a user object with an ID"""
    user = User(username="test", phone="+1234567890")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
```

### Frontend E2E

```typescript
// ❌ Bad
test('test1', async ({ page }) => {
  await page.goto('/');
  await page.click('button');
});

// ✅ Good
test('should submit login form when valid credentials provided', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Username').fill('testuser');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: /login/i }).click();

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText(/welcome/i)).toBeVisible();
});
```

### Test Data

```python
# ❌ Bad - Hard-coded values
def test_user():
    user = User(username="john", email="john@test.com")

# ✅ Good - Use factories or fixtures
@pytest.fixture
def test_user_data():
    return {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "phone": f"+91{random.randint(1000000000, 9999999999)}"
    }
```

---

## Troubleshooting

### Backend Tests Failing

**Issue:** Database connection errors

```bash
# Check database is running
docker ps | grep postgres

# Reset test database
docker exec -it gaming_postgres_test psql -U test_user -c "DROP DATABASE IF EXISTS gaming_test; CREATE DATABASE gaming_test;"
```

**Issue:** Import errors

```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

### E2E Tests Failing

**Issue:** Element not found

```typescript
// Use waitFor to wait for elements
await page.getByRole('button').waitFor({ state: 'visible' });

// Increase timeout
await expect(page.getByText('Hello')).toBeVisible({ timeout: 10000 });
```

**Issue:** Flaky tests

```typescript
// Wait for network idle
await page.goto('/dashboard', { waitUntil: 'networkidle' });

// Wait for specific API calls
await page.waitForResponse((response) =>
  response.url().includes('/api/v1/user') && response.status() === 200
);
```

### Load Tests Failing

**Issue:** High failure rate

- Check server logs
- Increase server resources
- Reduce spawn rate
- Check database connections

**Issue:** Timeouts

- Increase timeout in Locust
- Optimize slow endpoints
- Add caching
- Scale database

---

## Running All Tests

### Quick Test Suite

```bash
# Backend unit tests (fast)
cd backend && pytest -x

# Frontend E2E (critical paths only)
cd frontend && npx playwright test --grep @critical
```

### Full Test Suite

```bash
# Backend tests with coverage
cd backend
pytest --cov --cov-report=html

# Frontend E2E tests (all browsers)
cd frontend
npx playwright test

# Admin E2E tests
cd frontend-admin
npx playwright test

# Load tests (light load)
cd load-tests
locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 2m --headless
```

---

## Test Checklist

Before deployment:

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Code coverage >80%
- [ ] Load tests show acceptable performance
- [ ] Security scans pass
- [ ] No critical bugs in issue tracker
- [ ] Manual testing of critical flows completed

---

## Support

For testing issues:
- Check CI/CD logs on GitHub Actions
- Review test output and stack traces
- Check this guide for common issues
- Run tests locally with verbose output

---

**Last Updated:** November 16, 2025
**Next Review:** Before Production Launch
