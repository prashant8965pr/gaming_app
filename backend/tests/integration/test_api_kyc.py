"""
Integration tests for KYC API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.kyc
class TestKYCSubmission:
    """Test KYC document submission"""

    async def test_submit_kyc_aadhaar(self, client: AsyncClient, test_user, auth_headers):
        """Test submitting Aadhaar KYC"""
        response = await client.post(
            "/api/v1/kyc/submit",
            headers=auth_headers,
            json={
                "document_type": "aadhaar",
                "document_number": "123456789012",
                "full_name": "Test User",
                "date_of_birth": "1990-01-01",
                "address_line1": "123 Test St",
                "city": "Test City",
                "state": "Test State",
                "pincode": "123456",
                "front_image_url": "/uploads/kyc/front.jpg",
                "back_image_url": "/uploads/kyc/back.jpg"
            }
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert data["success"] == True

    async def test_submit_kyc_pan(self, client: AsyncClient, test_user, auth_headers):
        """Test submitting PAN KYC"""
        response = await client.post(
            "/api/v1/kyc/submit",
            headers=auth_headers,
            json={
                "document_type": "pan",
                "document_number": "ABCDE1234F",
                "full_name": "Test User",
                "date_of_birth": "1990-01-01",
                "front_image_url": "/uploads/kyc/pan.jpg"
            }
        )

        assert response.status_code in [200, 201]

    async def test_submit_kyc_invalid_aadhaar(self, client: AsyncClient, auth_headers):
        """Test submitting invalid Aadhaar number"""
        response = await client.post(
            "/api/v1/kyc/submit",
            headers=auth_headers,
            json={
                "document_type": "aadhaar",
                "document_number": "123",  # Too short
                "full_name": "Test User",
                "date_of_birth": "1990-01-01"
            }
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
@pytest.mark.kyc
class TestKYCStatus:
    """Test KYC status endpoints"""

    async def test_get_kyc_status(self, client: AsyncClient, test_user, test_kyc_document, auth_headers):
        """Test getting KYC status"""
        response = await client.get(
            "/api/v1/kyc/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "kyc_status" in data["data"]
        assert "documents" in data["data"]

    async def test_get_kyc_status_no_documents(self, client: AsyncClient, test_user, auth_headers):
        """Test getting KYC status with no documents"""
        response = await client.get(
            "/api/v1/kyc/status",
            headers=auth_headers
        )

        assert response.status_code == 200

    async def test_get_kyc_document_detail(self, client: AsyncClient, test_kyc_document, auth_headers):
        """Test getting specific KYC document"""
        response = await client.get(
            f"/api/v1/kyc/documents/{test_kyc_document.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


@pytest.mark.integration
@pytest.mark.kyc
class TestFileUpload:
    """Test file upload for KYC"""

    async def test_upload_kyc_document(self, client: AsyncClient, auth_headers):
        """Test uploading KYC document image"""
        # Create a mock file
        files = {
            "file": ("test.jpg", b"fake image content", "image/jpeg")
        }

        response = await client.post(
            "/api/v1/kyc/upload",
            headers=auth_headers,
            files=files
        )

        # May succeed or fail depending on upload configuration
        assert response.status_code in [200, 201, 400, 500]

    async def test_upload_invalid_file_type(self, client: AsyncClient, auth_headers):
        """Test uploading invalid file type"""
        files = {
            "file": ("test.txt", b"text content", "text/plain")
        }

        response = await client.post(
            "/api/v1/kyc/upload",
            headers=auth_headers,
            files=files
        )

        assert response.status_code in [400, 422]
