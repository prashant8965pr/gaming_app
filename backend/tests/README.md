# Testing Documentation

## Overview

Comprehensive test suite for the Gaming Platform API using pytest, pytest-asyncio, and pytest-cov.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── __init__.py
│   ├── test_models_user.py
│   ├── test_models_game.py
│   └── ...
├── integration/             # Integration tests for API endpoints
│   ├── __init__.py
│   ├── test_api_auth.py
│   ├── test_api_games.py
│   └── ...
└── fixtures/                # Additional test fixtures
    └── __init__.py
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only auth tests
pytest -m auth

# Run only game tests
pytest -m games
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/unit/test_models_user.py
pytest tests/integration/test_api_auth.py
```

### Run Specific Test Function
```bash
pytest tests/unit/test_models_user.py::TestUserModel::test_create_user
```

### Run with Verbose Output
```bash
pytest -v
pytest -vv  # Extra verbose
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.smoke` - Critical path tests
- `@pytest.mark.slow` - Tests that take significant time
- `@pytest.mark.auth` - Authentication related
- `@pytest.mark.wallet` - Wallet system tests
- `@pytest.mark.kyc` - KYC verification tests
- `@pytest.mark.rewards` - Rewards system tests
- `@pytest.mark.games` - Games system tests
- `@pytest.mark.admin` - Admin functionality tests

## Test Fixtures

### Database Fixtures

- `test_db_engine` - In-memory SQLite database engine
- `db_session` - Database session for tests
- `client` - Async HTTP client with database override

### User Fixtures

- `test_user` - Standard test user
- `test_user_2` - Second test user for multi-user tests
- `admin_user` - Admin user for admin tests
- `auth_token` - JWT token for test user
- `admin_token` - JWT token for admin user
- `auth_headers` - Authorization headers for requests
- `admin_headers` - Admin authorization headers

### Wallet Fixtures

- `test_wallets` - Set of wallets (cash, bonus, winnings) for test user

### Game Fixtures

- `test_game` - Test game catalog entry
- `test_game_session` - Active game session
- `sample_game_state` - Sample game state JSON
- `sample_move_data` - Sample move data

### KYC Fixtures

- `test_kyc_document` - Test KYC document

### Reward Fixtures

- `test_daily_bonus` - Test daily bonus record
- `test_achievement` - Test achievement

### Mock Fixtures

- `mock_payment_gateway` - Mocked payment gateway
- `mock_sms_service` - Mocked SMS service
- `mock_email_service` - Mocked email service

## Writing New Tests

### Unit Test Example

```python
import pytest
from models.user import User

@pytest.mark.unit
@pytest.mark.auth
class TestUserModel:
    async def test_create_user(self, db_session):
        """Test creating a new user"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed"
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPI:
    async def test_login(self, client: AsyncClient, test_user):
        """Test user login"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
```

## Best Practices

### 1. Test Organization
- Use descriptive test names
- Group related tests in classes
- Use appropriate markers
- Keep tests focused and atomic

### 2. Fixtures
- Use fixtures for common setup
- Leverage pytest's dependency injection
- Clean up resources properly
- Use appropriate fixture scopes

### 3. Assertions
- Use clear assertion messages
- Test both success and failure cases
- Validate response structure
- Check status codes and data

### 4. Async Tests
- Mark async tests with `async def`
- Use `await` for async operations
- Handle asyncio properly
- Use `pytest-asyncio` plugin

### 5. Database Tests
- Use in-memory database for speed
- Rollback after each test
- Don't rely on test order
- Test database constraints

### 6. API Tests
- Test authentication
- Test authorization
- Test validation
- Test error handling
- Test edge cases

## Coverage Goals

Target coverage metrics:

- **Overall Coverage**: > 80%
- **Models**: > 90%
- **Utils**: > 85%
- **API Endpoints**: > 75%
- **Services**: > 80%

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Nightly builds

## Troubleshooting

### Common Issues

**Issue**: Tests fail with database errors
**Solution**: Ensure test database is clean, check migrations

**Issue**: Async tests timeout
**Solution**: Check asyncio event loop configuration

**Issue**: Fixtures not found
**Solution**: Verify fixture is in conftest.py or imported

**Issue**: Coverage report missing files
**Solution**: Check .coveragerc configuration

## Test Data

### Test User Credentials
- Username: `testuser`
- Email: `test@example.com`
- Phone: `+919876543210`
- Password: `TestPass123!`

### Test Game
- Code: `ludo_test`
- Name: `Test Ludo`
- Entry Fee: Rs.100

### Test Session Code
- `TEST1234`

## Performance

- Unit tests should complete in < 100ms
- Integration tests should complete in < 1s
- Full test suite should complete in < 5 minutes

## Reporting Issues

When reporting test failures:
1. Include full error message
2. Specify Python version
3. Include test environment details
4. Provide steps to reproduce

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure tests pass locally
3. Achieve >80% coverage for new code
4. Update test documentation

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [HTTPX](https://www.python-httpx.org/)

---

**Last Updated**: November 16, 2025
**Test Coverage**: Phase 5 Implementation
**Status**: Active Development
