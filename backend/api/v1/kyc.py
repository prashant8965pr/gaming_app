"""
KYC API Endpoints
Handles KYC document submission, verification, and status
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import Dict, Any, List
from datetime import datetime
import uuid

from config.database import get_db
from config.settings import settings
from core.security import get_current_user
from core.exceptions import GamePlatformException
from models.user import User
from models.kyc import KYCDocument, KYCVerificationHistory
from schemas.kyc import (
    SubmitKYCRequest,
    KYCDocumentResponse,
    KYCStatusResponse,
    UploadKYCDocumentRequest
)
from utils.file_upload import file_upload_service

router = APIRouter()


# ============================================================================
# User KYC Endpoints
# ============================================================================

@router.post("/submit", response_model=Dict[str, Any])
async def submit_kyc_document(
    request_data: SubmitKYCRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit KYC document details
    User submits their document information before uploading images
    """
    try:
        # Check if user already has an approved KYC
        existing_approved = await db.execute(
            select(KYCDocument).where(
                and_(
                    KYCDocument.user_id == current_user.id,
                    KYCDocument.status == "approved"
                )
            )
        )
        if existing_approved.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="KYC already approved for this user"
            )

        # Check for pending KYC of same type
        existing_pending = await db.execute(
            select(KYCDocument).where(
                and_(
                    KYCDocument.user_id == current_user.id,
                    KYCDocument.document_type == request_data.document_type,
                    KYCDocument.status.in_(["pending", "under_review"])
                )
            )
        )
        if existing_pending.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a pending {request_data.document_type.upper()} verification"
            )

        # Create KYC document record
        kyc_document = KYCDocument(
            id=uuid.uuid4(),
            user_id=current_user.id,
            document_type=request_data.document_type,
            document_number=request_data.document_number,
            full_name=request_data.full_name,
            father_name=request_data.father_name,
            date_of_birth=datetime.combine(request_data.date_of_birth, datetime.min.time()),
            gender=request_data.gender,
            address=request_data.address,
            status="pending",
            ip_address=request.client.host if request.client else None
        )

        db.add(kyc_document)

        # Create verification history
        history = KYCVerificationHistory(
            id=uuid.uuid4(),
            user_id=current_user.id,
            kyc_document_id=kyc_document.id,
            action="submitted",
            new_status="pending",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        db.add(history)
        await db.commit()
        await db.refresh(kyc_document)

        return {
            "success": True,
            "data": {
                "kyc_id": str(kyc_document.id),
                "status": kyc_document.status,
                "message": "KYC details submitted successfully. Please upload required documents.",
                "required_uploads": _get_required_uploads(request_data.document_type)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit KYC: {str(e)}"
        )


@router.post("/upload", response_model=Dict[str, Any])
async def upload_kyc_document_image(
    kyc_id: str,
    document_side: str,  # front, back, selfie
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload KYC document image (front, back, or selfie)
    """
    try:
        # Validate document_side
        if document_side not in ['front', 'back', 'selfie']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document_side must be 'front', 'back', or 'selfie'"
            )

        # Get KYC document
        result = await db.execute(
            select(KYCDocument).where(KYCDocument.id == uuid.UUID(kyc_id))
        )
        kyc_document = result.scalar_one_or_none()

        if not kyc_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC document not found"
            )

        # Verify ownership
        if kyc_document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload to this KYC document"
            )

        # Check if KYC is already approved
        if kyc_document.status == "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot upload documents to approved KYC"
            )

        # Upload file
        success, file_url, error = await file_upload_service.upload_kyc_document(
            file=file,
            user_id=str(current_user.id),
            document_type=kyc_document.document_type,
            document_side=document_side
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "File upload failed"
            )

        # Update KYC document with file URL
        if document_side == 'front':
            kyc_document.document_front_url = file_url
        elif document_side == 'back':
            kyc_document.document_back_url = file_url
        elif document_side == 'selfie':
            kyc_document.selfie_url = file_url

        # Check if all required documents are uploaded
        if _all_documents_uploaded(kyc_document):
            kyc_document.status = "under_review"

            # Create history entry
            history = KYCVerificationHistory(
                id=uuid.uuid4(),
                user_id=current_user.id,
                kyc_document_id=kyc_document.id,
                action="documents_uploaded",
                old_status="pending",
                new_status="under_review"
            )
            db.add(history)

        await db.commit()
        await db.refresh(kyc_document)

        return {
            "success": True,
            "data": {
                "message": f"{document_side.capitalize()} uploaded successfully",
                "file_url": file_url,
                "kyc_status": kyc_document.status,
                "pending_uploads": _get_pending_uploads(kyc_document)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_kyc_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's KYC status and documents
    """
    try:
        # Get all KYC documents for user
        result = await db.execute(
            select(KYCDocument)
            .where(KYCDocument.user_id == current_user.id)
            .order_by(KYCDocument.created_at.desc())
        )
        kyc_documents = result.scalars().all()

        # Check if any document is approved
        kyc_completed = any(doc.status == "approved" for doc in kyc_documents)

        # Get pending actions
        pending_actions = []
        for doc in kyc_documents:
            if doc.status in ["pending", "under_review"]:
                pending_actions.extend(_get_pending_uploads(doc))

        # Convert to response format
        documents_response = []
        for doc in kyc_documents:
            documents_response.append(KYCDocumentResponse(
                id=str(doc.id),
                user_id=str(doc.user_id),
                document_type=doc.document_type,
                document_number=_mask_document_number(doc.document_number, doc.document_type),
                full_name=doc.full_name,
                date_of_birth=doc.date_of_birth,
                status=doc.status,
                document_front_url=doc.document_front_url,
                document_back_url=doc.document_back_url,
                selfie_url=doc.selfie_url,
                rejection_reason=doc.rejection_reason,
                submitted_at=doc.submitted_at,
                reviewed_at=doc.reviewed_at,
                created_at=doc.created_at
            ))

        return {
            "success": True,
            "data": {
                "kyc_completed": kyc_completed,
                "kyc_status": current_user.kyc_status,
                "kyc_documents": documents_response,
                "pending_actions": pending_actions
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get KYC status: {str(e)}"
        )


@router.get("/documents", response_model=Dict[str, Any])
async def list_kyc_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all KYC documents submitted by user
    """
    try:
        result = await db.execute(
            select(KYCDocument)
            .where(KYCDocument.user_id == current_user.id)
            .order_by(KYCDocument.created_at.desc())
        )
        documents = result.scalars().all()

        documents_response = []
        for doc in documents:
            documents_response.append(KYCDocumentResponse(
                id=str(doc.id),
                user_id=str(doc.user_id),
                document_type=doc.document_type,
                document_number=_mask_document_number(doc.document_number, doc.document_type),
                full_name=doc.full_name,
                date_of_birth=doc.date_of_birth,
                status=doc.status,
                document_front_url=doc.document_front_url,
                document_back_url=doc.document_back_url,
                selfie_url=doc.selfie_url,
                rejection_reason=doc.rejection_reason,
                submitted_at=doc.submitted_at,
                reviewed_at=doc.reviewed_at,
                created_at=doc.created_at
            ))

        return {
            "success": True,
            "data": {
                "documents": documents_response,
                "total_count": len(documents_response)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _get_required_uploads(document_type: str) -> List[str]:
    """Get list of required uploads for document type"""
    if document_type == "aadhaar":
        return ["front", "back", "selfie"]
    elif document_type == "pan":
        return ["front", "selfie"]
    elif document_type in ["voter_id", "driving_license", "passport"]:
        return ["front", "back", "selfie"]
    return ["front", "selfie"]


def _all_documents_uploaded(kyc_document: KYCDocument) -> bool:
    """Check if all required documents are uploaded"""
    required = _get_required_uploads(kyc_document.document_type)

    if "front" in required and not kyc_document.document_front_url:
        return False
    if "back" in required and not kyc_document.document_back_url:
        return False
    if "selfie" in required and not kyc_document.selfie_url:
        return False

    return True


def _get_pending_uploads(kyc_document: KYCDocument) -> List[str]:
    """Get list of pending uploads for KYC document"""
    if kyc_document.status in ["approved", "rejected"]:
        return []

    required = _get_required_uploads(kyc_document.document_type)
    pending = []

    if "front" in required and not kyc_document.document_front_url:
        pending.append(f"Upload {kyc_document.document_type} front image")
    if "back" in required and not kyc_document.document_back_url:
        pending.append(f"Upload {kyc_document.document_type} back image")
    if "selfie" in required and not kyc_document.selfie_url:
        pending.append(f"Upload selfie for verification")

    return pending


def _mask_document_number(document_number: str, document_type: str) -> str:
    """Mask document number for security"""
    if not document_number:
        return ""

    if document_type == "aadhaar":
        # Show only last 4 digits: XXXX-XXXX-1234
        return f"XXXX-XXXX-{document_number[-4:]}"
    elif document_type == "pan":
        # Show only last 4 characters: XXXXXX1234
        return f"XXXXXX{document_number[-4:]}"
    else:
        # Generic masking: show last 4 characters
        return f"{'X' * (len(document_number) - 4)}{document_number[-4:]}"
