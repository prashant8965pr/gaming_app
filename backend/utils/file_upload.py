"""
File Upload Utility
Handles file uploads to local storage or cloud storage (AWS S3/Cloudinary)
"""
import os
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from config.settings import settings
import hashlib


class FileUploadService:
    """Service for handling file uploads"""

    # Allowed file types for KYC documents
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/webp'
    }

    ALLOWED_DOCUMENT_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
        'application/pdf'
    }

    # Max file size: 5 MB
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(self):
        self.storage_type = getattr(settings, 'FILE_STORAGE_TYPE', 'local')  # local, s3, cloudinary
        self.upload_dir = Path(getattr(settings, 'UPLOAD_DIR', '/app/uploads'))

        # Create upload directories if using local storage
        if self.storage_type == 'local':
            self._create_upload_dirs()

    def _create_upload_dirs(self):
        """Create upload directories for local storage"""
        dirs = [
            self.upload_dir / 'kyc' / 'aadhaar',
            self.upload_dir / 'kyc' / 'pan',
            self.upload_dir / 'kyc' / 'selfie',
            self.upload_dir / 'avatars',
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    async def validate_file(
        self,
        file: UploadFile,
        allowed_types: set = None,
        max_size: int = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        if allowed_types is None:
            allowed_types = self.ALLOWED_IMAGE_TYPES

        if max_size is None:
            max_size = self.MAX_FILE_SIZE

        # Check content type
        if file.content_type not in allowed_types:
            return False, f"Invalid file type. Allowed types: {', '.join(allowed_types)}"

        # Read file to check size
        file_content = await file.read()
        file_size = len(file_content)

        # Reset file pointer
        await file.seek(0)

        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"File size exceeds {max_size_mb:.1f} MB limit"

        if file_size == 0:
            return False, "File is empty"

        return True, None

    def _generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename with timestamp and UUID"""
        ext = Path(original_filename).suffix.lower()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]

        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        return f"{timestamp}_{unique_id}{ext}"

    async def upload_kyc_document(
        self,
        file: UploadFile,
        user_id: str,
        document_type: str,
        document_side: str  # front, back, selfie
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload KYC document
        Returns: (success, file_url, error_message)
        """
        # Validate file
        is_valid, error = await self.validate_file(file, self.ALLOWED_IMAGE_TYPES)
        if not is_valid:
            return False, None, error

        try:
            # Generate filename
            filename = self._generate_unique_filename(
                file.filename,
                prefix=f"{user_id}_{document_type}_{document_side}"
            )

            if self.storage_type == 'local':
                return await self._upload_to_local(file, 'kyc', document_type, filename)
            elif self.storage_type == 's3':
                return await self._upload_to_s3(file, f'kyc/{document_type}', filename)
            elif self.storage_type == 'cloudinary':
                return await self._upload_to_cloudinary(file, f'kyc/{document_type}', filename)
            else:
                return False, None, "Invalid storage configuration"

        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"

    async def upload_avatar(
        self,
        file: UploadFile,
        user_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload user avatar
        Returns: (success, file_url, error_message)
        """
        # Validate file
        is_valid, error = await self.validate_file(file, self.ALLOWED_IMAGE_TYPES)
        if not is_valid:
            return False, None, error

        try:
            # Generate filename
            filename = self._generate_unique_filename(
                file.filename,
                prefix=f"avatar_{user_id}"
            )

            if self.storage_type == 'local':
                return await self._upload_to_local(file, 'avatars', '', filename)
            elif self.storage_type == 's3':
                return await self._upload_to_s3(file, 'avatars', filename)
            elif self.storage_type == 'cloudinary':
                return await self._upload_to_cloudinary(file, 'avatars', filename)
            else:
                return False, None, "Invalid storage configuration"

        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"

    async def _upload_to_local(
        self,
        file: UploadFile,
        category: str,
        subcategory: str,
        filename: str
    ) -> Tuple[bool, str, None]:
        """Upload file to local storage"""
        # Create path
        if subcategory:
            file_path = self.upload_dir / category / subcategory / filename
        else:
            file_path = self.upload_dir / category / filename

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Return URL (relative path)
        if subcategory:
            file_url = f"/uploads/{category}/{subcategory}/{filename}"
        else:
            file_url = f"/uploads/{category}/{filename}"

        return True, file_url, None

    async def _upload_to_s3(
        self,
        file: UploadFile,
        folder: str,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload file to AWS S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError

            # Get S3 credentials from settings
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

            bucket_name = settings.AWS_S3_BUCKET
            key = f"{folder}/{filename}"

            # Read file content
            file_content = await file.read()

            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_content,
                ContentType=file.content_type
            )

            # Generate URL
            file_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

            return True, file_url, None

        except ClientError as e:
            return False, None, f"S3 upload failed: {str(e)}"
        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"

    async def _upload_to_cloudinary(
        self,
        file: UploadFile,
        folder: str,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload file to Cloudinary"""
        try:
            import cloudinary
            import cloudinary.uploader

            # Configure Cloudinary
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )

            # Read file content
            file_content = await file.read()

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                folder=folder,
                public_id=Path(filename).stem,
                resource_type="auto"
            )

            file_url = result['secure_url']

            return True, file_url, None

        except Exception as e:
            return False, None, f"Cloudinary upload failed: {str(e)}"

    async def delete_file(self, file_url: str) -> bool:
        """Delete file from storage"""
        try:
            if self.storage_type == 'local':
                # Extract path from URL
                file_path = self.upload_dir / file_url.lstrip('/uploads/')
                if file_path.exists():
                    file_path.unlink()
                return True

            elif self.storage_type == 's3':
                # Extract key from URL and delete from S3
                import boto3
                # Implementation here
                return True

            elif self.storage_type == 'cloudinary':
                # Delete from Cloudinary
                import cloudinary.uploader
                # Implementation here
                return True

        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_hash(self, file_content: bytes) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()


# Singleton instance
file_upload_service = FileUploadService()
