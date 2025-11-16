"""
Load Testing with Locust
Performance testing for Gaming Platform API
"""

from locust import HttpUser, task, between
import random
import json


class GamingPlatformUser(HttpUser):
    """
    Simulates a user interacting with the gaming platform
    """

    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)

    # Base URL will be set via command line
    # locust -f locustfile.py --host=http://localhost:8000

    def on_start(self):
        """
        Called when a user starts
        Perform login to get auth token
        """
        self.phone = f"+9198765432{random.randint(10, 99)}"
        self.token = None
        self.user_id = None

        # Send OTP
        response = self.client.post(
            "/api/v1/auth/send-otp",
            json={"phone": self.phone},
            name="/auth/send-otp"
        )

        if response.status_code == 200:
            # In real scenario, we'd need actual OTP
            # For load testing, we might mock this
            pass

    @task(5)
    def view_game_catalog(self):
        """View available games"""
        self.client.get(
            "/api/v1/games/catalog",
            name="/games/catalog"
        )

    @task(3)
    def view_active_sessions(self):
        """View active game sessions"""
        self.client.get(
            "/api/v1/games/sessions/active",
            name="/games/sessions/active"
        )

    @task(2)
    def check_wallet_balance(self):
        """Check wallet balance"""
        if self.token:
            self.client.get(
                "/api/v1/wallet/balance",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/wallet/balance"
            )

    @task(2)
    def view_transaction_history(self):
        """View transaction history"""
        if self.token:
            self.client.get(
                "/api/v1/wallet/transactions?skip=0&limit=20",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/wallet/transactions"
            )

    @task(1)
    def create_game_session(self):
        """Create a new game session"""
        if self.token:
            self.client.post(
                "/api/v1/games/sessions",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "game_id": "test-game-uuid",
                    "entry_fee": 100,
                    "max_players": 4,
                    "is_private": False
                },
                name="/games/sessions [POST]"
            )

    @task(2)
    def view_leaderboard(self):
        """View leaderboard"""
        self.client.get(
            "/api/v1/rewards/leaderboard?period=weekly&limit=100",
            name="/rewards/leaderboard"
        )

    @task(1)
    def view_user_achievements(self):
        """View user achievements"""
        if self.token:
            self.client.get(
                "/api/v1/rewards/achievements",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/rewards/achievements"
            )


class AdminUser(HttpUser):
    """
    Simulates an admin user
    """

    wait_time = between(2, 10)

    def on_start(self):
        """Login as admin"""
        self.token = None

        # Mock admin login
        response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+919876543210",
                "otp": "123456",
                "device_id": "load-test-device",
                "device_name": "Locust",
                "device_os": "Python"
            },
            name="/auth/verify-otp [Admin]"
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.token = data["data"]["tokens"]["access_token"]

    @task(5)
    def view_dashboard_stats(self):
        """View admin dashboard statistics"""
        if self.token:
            self.client.get(
                "/api/v1/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/admin/dashboard/stats"
            )

    @task(3)
    def view_pending_kyc(self):
        """View pending KYC documents"""
        if self.token:
            self.client.get(
                "/api/v1/admin/kyc/pending?skip=0&limit=20",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/admin/kyc/pending"
            )

    @task(3)
    def view_pending_withdrawals(self):
        """View pending withdrawals"""
        if self.token:
            self.client.get(
                "/api/v1/admin/withdrawals/pending?skip=0&limit=20",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/admin/withdrawals/pending"
            )

    @task(2)
    def view_all_users(self):
        """View all users"""
        if self.token:
            self.client.get(
                "/api/v1/admin/users?skip=0&limit=50",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/admin/users"
            )


class HighLoadScenario(HttpUser):
    """
    Simulates high concurrent load
    Mixed user behavior
    """

    wait_time = between(0.5, 2)

    tasks = {
        GamingPlatformUser: 8,  # 80% regular users
        AdminUser: 2,  # 20% admin users
    }


# Run configurations:
#
# Basic load test:
# locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2
#
# Stress test:
# locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
#
# Spike test:
# locust -f locustfile.py --host=http://localhost:8000 --users 500 --spawn-rate 50 --run-time 2m
#
# Soak test:
# locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 1h
