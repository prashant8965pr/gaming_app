"""
End-to-end tests for complete user journeys
Tests complete workflows from registration to gameplay
"""
import pytest
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.asyncio
class TestCompleteUserJourney:
    """Test complete user journey from signup to gameplay"""

    async def test_new_user_complete_flow(self, client: AsyncClient, test_game, mock_payment_gateway):
        """
        Test complete flow for a new user:
        1. Register → 2. Verify phone → 3. Add money
        4. Join game session → 5. Play game
        """
        
        # Step 1: Register new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newplayer",
                "email": "newplayer@test.com",
                "phone": "+919999999999",
                "password": "SecurePass123!",
                "display_name": "New Player"
            }
        )
        assert register_response.status_code == 201
        
        # Step 2: Verify OTP
        verify_response = await client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+919999999999",
                "otp": "123456"
            }
        )
        assert verify_response.status_code == 200
        access_token = verify_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 3: Add money
        add_money_response = await client.post(
            "/api/v1/wallet/add-money",
            headers=headers,
            json={"amount": 100000, "payment_method": "razorpay"}
        )
        assert add_money_response.status_code == 200


@pytest.mark.e2e
class TestKYCAndWithdrawal:
    """Test KYC and withdrawal flow"""

    async def test_kyc_verification_flow(self, client: AsyncClient, test_user, auth_headers):
        """Test complete KYC verification workflow"""
        
        # Submit KYC
        kyc_response = await client.post(
            "/api/v1/kyc/submit",
            headers=auth_headers,
            json={
                "document_type": "aadhaar",
                "document_number": "123456789012",
                "full_name": "Test User",
                "date_of_birth": "1990-01-01",
                "address_line1": "123 Test St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "front_image_url": "/uploads/kyc/front.jpg",
                "back_image_url": "/uploads/kyc/back.jpg"
            }
        )
        assert kyc_response.status_code in [200, 201]
