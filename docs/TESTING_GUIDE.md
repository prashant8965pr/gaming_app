# Gaming Platform - Testing Guide

Complete guide for testing the Gaming Platform backend API and Flutter mobile application.

## Table of Contents

1. [Overview](#overview)
2. [Testing Stack](#testing-stack)
3. [Backend Testing](#backend-testing)
4. [Mobile App Testing](#mobile-app-testing)
5. [API Testing](#api-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Performance Testing](#performance-testing)
8. [Security Testing](#security-testing)
9. [CI/CD Integration](#cicd-integration)
10. [Best Practices](#best-practices)

## Overview

The Gaming Platform uses a comprehensive testing strategy covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete user journey testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing

## Testing Stack

### Backend
- **pytest**: Test framework
- **httpx**: Async HTTP client for API testing
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage
- **faker**: Test data generation
- **factory-boy**: Model factories

### Mobile
- **flutter_test**: Flutter testing framework
- **mockito**: Mocking framework
- **integration_test**: Flutter integration tests
- **golden_toolkit**: UI snapshot testing

### Tools
- **Postman/Thunder Client**: API manual testing
- **Locust**: Load testing
- **OWASP ZAP**: Security testing
- **SonarQube**: Code quality analysis

## Backend Testing

### Setup Test Environment

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # E2E tests only
```

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_models_user.py
│   ├── test_models_game.py
│   └── ...
├── integration/             # Integration tests
│   ├── test_api_auth.py
│   ├── test_api_games.py
│   ├── test_api_wallet.py
│   ├── test_api_rewards.py
│   └── test_api_kyc.py
├── e2e/                     # End-to-end tests
│   └── test_user_journey.py
└── fixtures/                # Test data fixtures
    └── __init__.py
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from models.user import User
from services.auth_service import hash_password

@pytest.mark.unit
def test_user_creation():
    """Test user model creation"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123")
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
```

#### Integration Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    assert "user" in response.json()["data"]
```

#### E2E Test Example

```python
@pytest.mark.e2e
async def test_complete_user_flow(client: AsyncClient):
    """Test complete user registration to gameplay"""
    # Register
    register_response = await client.post("/api/v1/auth/register", ...)
    
    # Login
    login_response = await client.post("/api/v1/auth/login", ...)
    
    # Add money
    add_money_response = await client.post("/api/v1/wallet/add-money", ...)
    
    # Join game
    join_response = await client.post("/api/v1/games/sessions/join", ...)
```

### Test Coverage Goals

- **Overall Coverage**: ≥ 80%
- **Critical Paths**: ≥ 95%
- **Authentication**: 100%
- **Payment Processing**: 100%
- **Game Logic**: ≥ 90%

### Running Tests with Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/integration/test_api_auth.py

# Run specific test function
pytest tests/integration/test_api_auth.py::test_register_user

# Run tests matching pattern
pytest -k "auth"

# Parallel execution
pytest -n auto

# Generate HTML report
pytest --html=report.html
```

## Mobile App Testing

### Setup Test Environment

```bash
cd mobile_app

# Get dependencies
flutter pub get

# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# View coverage
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### Test Structure

```
mobile_app/test/
├── unit/
│   ├── data/
│   │   ├── repositories_test.dart
│   │   └── datasources_test.dart
│   ├── domain/
│   │   └── usecases_test.dart
│   └── presentation/
│       └── blocs_test.dart
├── widget/
│   ├── auth_test.dart
│   ├── wallet_test.dart
│   └── games_test.dart
└── integration/
    └── app_test.dart
```

### Writing Flutter Tests

#### Unit Test Example

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('AuthRepository', () {
    test('login returns success on valid credentials', () async {
      final repository = AuthRepository();
      
      final result = await repository.login(
        username: 'testuser',
        password: 'password123',
      );
      
      expect(result.isRight(), true);
    });
  });
}
```

#### Widget Test Example

```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Login screen shows email and password fields', 
    (WidgetTester tester) async {
    
    await tester.pumpWidget(MyApp());
    
    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.text('Login'), findsOneWidget);
  });
}
```

#### Integration Test Example

```dart
import 'package:integration_test/integration_test.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Complete user flow', (WidgetTester tester) async {
    // Launch app
    await tester.pumpWidget(MyApp());
    
    // Login
    await tester.enterText(find.byKey(Key('username')), 'testuser');
    await tester.enterText(find.byKey(Key('password')), 'password123');
    await tester.tap(find.text('Login'));
    await tester.pumpAndSettle();
    
    // Verify navigation to home
    expect(find.text('Home'), findsOneWidget);
  });
}
```

### Running Mobile Tests

```bash
# Unit and widget tests
flutter test

# Integration tests
flutter test integration_test/

# Specific test file
flutter test test/unit/auth_test.dart

# With coverage
flutter test --coverage

# On device
flutter drive --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart
```

## API Testing

### Postman Collection

Import the collection: `backend/tests/Gaming_Platform_API.postman_collection.json`

#### Quick Start

1. **Import Collection**
   - Open Postman
   - Import → Upload Files
   - Select `Gaming_Platform_API.postman_collection.json`

2. **Set Environment Variables**
   ```
   base_url: http://localhost:8000
   access_token: (auto-set after login)
   user_id: (auto-set after login)
   ```

3. **Run Collection**
   - Collection Runner → Select collection
   - Run automated tests

#### Manual Testing Flow

1. **Authentication** → Register → Login (token auto-saved)
2. **Games** → Browse games → Create session
3. **Wallet** → Add money → Verify payment
4. **Rewards** → Check daily bonus → View achievements
5. **KYC** → Submit documents → Check status

### Thunder Client (VS Code)

1. Install Thunder Client extension
2. Import collection JSON
3. Set environment variables
4. Run requests

### cURL Examples

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Get wallet balance (with auth)
curl -X GET http://localhost:8000/api/v1/wallet/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## End-to-End Testing

E2E tests verify complete user workflows:

### Test Scenarios

1. **New User Journey**
   - Registration → Verification → Wallet setup → First game

2. **Payment Flow**
   - Add money → Verify payment → Transaction history

3. **KYC Process**
   - Document submission → Verification → Withdrawal

4. **Referral Program**
   - Get code → Refer friend → Receive bonus

5. **Multiplayer Game**
   - Create session → Players join → Game starts → Winner determined

### Running E2E Tests

```bash
# Backend E2E
cd backend
pytest -m e2e -v

# Mobile E2E
cd mobile_app
flutter drive --driver=test_driver/integration_test.dart \
  --target=integration_test/complete_flow_test.dart

# Full system E2E (requires both running)
./scripts/run-e2e-tests.sh
```

## Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class GameUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        self.token = response.json()["data"]["access_token"]
    
    @task(3)
    def get_games(self):
        self.client.get("/api/v1/games", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def get_wallet(self):
        self.client.get("/api/v1/wallet/balance", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Performance Targets

- **API Response Time**: < 200ms (p95)
- **Database Queries**: < 50ms average
- **Concurrent Users**: 10,000+
- **Requests per Second**: 1,000+
- **Error Rate**: < 0.1%

## Security Testing

### OWASP ZAP Testing

```bash
# Automated scan
zap-cli quick-scan -s all http://localhost:8000

# Full scan
zap-cli active-scan http://localhost:8000/api/v1/*
```

### Security Checklist

- [ ] SQL Injection protection
- [ ] XSS prevention
- [ ] CSRF tokens
- [ ] Authentication bypass attempts
- [ ] Authorization checks
- [ ] Rate limiting
- [ ] Input validation
- [ ] Secure headers
- [ ] Secrets in code
- [ ] Dependency vulnerabilities

### Manual Security Tests

```bash
# Test SQL injection
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username": "admin'\'' OR '\''1'\''='\''1", "password": "test"}'

# Test XSS
curl -X POST http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer TOKEN" \
  -d '{"display_name": "<script>alert(1)</script>"}'

# Test rate limiting
for i in {1..100}; do
  curl http://localhost:8000/api/v1/auth/login
done
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Every push to main
- Every pull request
- Scheduled daily runs

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  mobile-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - name: Run tests
        run: |
          cd mobile_app
          flutter test --coverage
```

## Best Practices

### General

1. **Write tests first** (TDD approach)
2. **Keep tests independent** - no test dependencies
3. **Use meaningful names** - describe what is being tested
4. **Test edge cases** - not just happy paths
5. **Mock external services** - don't depend on third parties
6. **Keep tests fast** - unit tests should run in milliseconds
7. **Clean up after tests** - reset database, clear caches
8. **Use fixtures** - DRY principle for test data
9. **Document complex tests** - explain the why, not the what
10. **Review test failures** - don't ignore failing tests

### Test Organization

```python
# Good test structure
def test_user_registration_with_valid_data_creates_new_user():
    """
    Given: Valid user registration data
    When: POST /api/v1/auth/register is called
    Then: New user is created with status 201
    """
    # Arrange
    user_data = {...}
    
    # Act
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert "user" in response.json()["data"]
```

### Coverage Guidelines

- Aim for high coverage but don't obsess over 100%
- Focus on critical business logic
- Don't test framework code
- Test error handling and edge cases
- Review uncovered lines regularly

### Common Pitfalls

❌ **Don't:**
- Test implementation details
- Write flaky tests
- Share state between tests
- Test too many things in one test
- Ignore slow tests
- Skip writing tests for bug fixes

✅ **Do:**
- Test behavior, not implementation
- Make tests deterministic
- Isolate tests completely
- One assertion per test (when possible)
- Optimize slow tests
- Add regression tests for bugs

## Troubleshooting

### Common Issues

**Tests fail locally but pass in CI:**
- Check environment variables
- Verify dependencies versions
- Check database state

**Flaky tests:**
- Add proper waits for async operations
- Fix race conditions
- Remove dependency on external services

**Slow tests:**
- Use fixtures efficiently
- Mock heavy operations
- Run tests in parallel

**Low coverage:**
- Identify untested areas
- Prioritize critical paths
- Add integration tests

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Flutter Testing](https://flutter.dev/docs/testing)
- [Postman Learning](https://learning.postman.com/)
- [Locust Documentation](https://docs.locust.io/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## Support

For testing issues:
1. Check this guide first
2. Review test logs
3. Check CI/CD pipeline
4. Consult team documentation
5. Ask in team chat

---

**Last Updated**: 2025-11-17  
**Maintainers**: Development Team
