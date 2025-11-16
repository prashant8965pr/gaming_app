"""
Integration tests for Authentication API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRegister:
    """Test user registration"""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser123",
                "email": "newuser@test.com",
                "phone": "+919876543299",
                "password": "SecurePass123!",
                "display_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] == True
        assert "user" in data["data"]
        assert data["data"]["user"]["username"] == "newuser123"

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with duplicate username"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,
                "email": "different@test.com",
                "phone": "+919876543298",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": test_user.email,
                "phone": "+919876543297",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 400

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@test.com",
                "phone": "+919876543296",
                "password": "weak"
            }
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
@pytest.mark.auth
class TestAuthLogin:
    """Test user login"""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]
        assert "user" in data["data"]

    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "SomePassword123!"
            }
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
class TestAuthMe:
    """Test get current user"""

    async def test_get_current_user(self, client: AsyncClient, test_user, auth_headers):
        """Test getting current user details"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["user"]["id"] == str(test_user.id)
        assert data["data"]["user"]["username"] == test_user.username

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without auth"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
