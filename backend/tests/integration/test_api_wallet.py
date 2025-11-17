"""
Integration tests for Wallet API
"""
import pytest
from httpx import AsyncClient
from decimal import Decimal


@pytest.mark.integration
@pytest.mark.wallet
class TestWalletBalance:
    """Test wallet balance endpoints"""

    async def test_get_wallet_balance(self, client: AsyncClient, test_user, test_wallets, auth_headers):
        """Test getting wallet balance"""
        response = await client.get(
            "/api/v1/wallet/balance",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "wallets" in data["data"]
        assert len(data["data"]["wallets"]) == 3  # cash, bonus, winnings

    async def test_get_wallet_balance_unauthorized(self, client: AsyncClient):
        """Test getting wallet balance without auth"""
        response = await client.get("/api/v1/wallet/balance")
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.wallet
class TestAddMoney:
    """Test add money endpoints"""

    async def test_initiate_add_money(self, client: AsyncClient, test_user, test_wallets, auth_headers, mock_payment_gateway):
        """Test initiating add money transaction"""
        response = await client.post(
            "/api/v1/wallet/add-money",
            headers=auth_headers,
            json={
                "amount": 50000,  # Rs.500
                "payment_method": "razorpay"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "order_id" in data["data"]
        assert "transaction_id" in data["data"]

    async def test_add_money_invalid_amount(self, client: AsyncClient, auth_headers):
        """Test add money with invalid amount"""
        response = await client.post(
            "/api/v1/wallet/add-money",
            headers=auth_headers,
            json={
                "amount": 50,  # Below minimum
                "payment_method": "razorpay"
            }
        )

        assert response.status_code == 400

    async def test_add_money_verify_success(self, client: AsyncClient, test_user, test_wallets, auth_headers, mock_payment_gateway):
        """Test verifying successful payment"""
        # First initiate
        init_response = await client.post(
            "/api/v1/wallet/add-money",
            headers=auth_headers,
            json={"amount": 50000, "payment_method": "razorpay"}
        )
        transaction_id = init_response.json()["data"]["transaction_id"]

        # Then verify
        verify_response = await client.post(
            "/api/v1/wallet/verify-payment",
            headers=auth_headers,
            json={
                "transaction_id": transaction_id,
                "payment_id": "TEST_PAY_123",
                "signature": "test_signature"
            }
        )

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["success"] == True


@pytest.mark.integration
@pytest.mark.wallet
class TestWithdraw:
    """Test withdraw money endpoints"""

    async def test_initiate_withdrawal(self, client: AsyncClient, test_user, test_wallets, auth_headers):
        """Test initiating withdrawal"""
        response = await client.post(
            "/api/v1/wallet/withdraw",
            headers=auth_headers,
            json={
                "amount": 10000,  # Rs.100
                "bank_account_id": "test_bank_id",
                "withdrawal_method": "bank_transfer"
            }
        )

        assert response.status_code in [200, 201]

    async def test_withdrawal_insufficient_balance(self, client: AsyncClient, test_user, test_wallets, auth_headers):
        """Test withdrawal with insufficient balance"""
        response = await client.post(
            "/api/v1/wallet/withdraw",
            headers=auth_headers,
            json={
                "amount": 999999999,  # More than available
                "bank_account_id": "test_bank_id",
                "withdrawal_method": "bank_transfer"
            }
        )

        assert response.status_code == 400

    async def test_withdrawal_below_minimum(self, client: AsyncClient, auth_headers):
        """Test withdrawal below minimum amount"""
        response = await client.post(
            "/api/v1/wallet/withdraw",
            headers=auth_headers,
            json={
                "amount": 50,  # Below minimum
                "bank_account_id": "test_bank_id",
                "withdrawal_method": "bank_transfer"
            }
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.wallet
class TestTransactionHistory:
    """Test transaction history endpoints"""

    async def test_get_transaction_history(self, client: AsyncClient, test_user, test_wallets, auth_headers):
        """Test getting transaction history"""
        response = await client.get(
            "/api/v1/wallet/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "transactions" in data["data"]
        assert isinstance(data["data"]["transactions"], list)

    async def test_get_transaction_history_with_filters(self, client: AsyncClient, auth_headers):
        """Test transaction history with filters"""
        response = await client.get(
            "/api/v1/wallet/transactions?type=deposit&limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    async def test_get_transaction_detail(self, client: AsyncClient, auth_headers):
        """Test getting single transaction detail"""
        # This would need an actual transaction ID in a real test
        response = await client.get(
            "/api/v1/wallet/transactions/test_transaction_id",
            headers=auth_headers
        )

        # Expecting 404 since transaction doesn't exist
        assert response.status_code in [200, 404]
