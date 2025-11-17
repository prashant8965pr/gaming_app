"""
Tournament API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from config.database import get_db
from middleware.auth import get_current_user
from models.tournament import Tournament, TournamentRegistration
from models.user import User
from services.tournament_service import TournamentService

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


# Schemas
class TournamentCreate(BaseModel):
    name: str
    description: str = None
    game_id: str
    tournament_type: str = "single_elimination"
    entry_fee: int
    max_participants: int = 16
    min_participants: int = 4
    start_time: datetime
    registration_start: datetime
    registration_end: datetime
    prize_distribution: dict = {"1st": 50, "2nd": 30, "3rd": 20}
    rules: dict = None
    is_featured: bool = False


@router.get("")
async def get_tournaments(
    status: str = None,
    game_id: str = None,
    is_featured: bool = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of tournaments"""
    query = db.query(Tournament)
    
    if status:
        query = query.filter(Tournament.status == status)
    if game_id:
        query = query.filter(Tournament.game_id == game_id)
    if is_featured is not None:
        query = query.filter(Tournament.is_featured == is_featured)
    
    tournaments = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": {
            "tournaments": [t.to_dict() for t in tournaments],
            "total": query.count()
        }
    }


@router.get("/{tournament_id}")
async def get_tournament(tournament_id: str, db: Session = Depends(get_db)):
    """Get tournament details"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    return {
        "success": True,
        "data": {"tournament": tournament.to_dict()}
    }


@router.post("")
async def create_tournament(
    tournament_data: TournamentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new tournament (admin only)"""
    try:
        tournament = TournamentService.create_tournament(
            db,
            tournament_data.dict(),
            str(current_user.id)
        )
        return {
            "success": True,
            "data": {"tournament": tournament.to_dict()}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{tournament_id}/register")
async def register_tournament(
    tournament_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for tournament"""
    try:
        registration = TournamentService.register_for_tournament(
            db,
            tournament_id,
            str(current_user.id)
        )
        return {
            "success": True,
            "data": {"registration": registration.to_dict()}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tournament_id}/bracket")
async def get_bracket(tournament_id: str, db: Session = Depends(get_db)):
    """Get tournament bracket"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    return {
        "success": True,
        "data": {"bracket": tournament.bracket_data}
    }


@router.post("/{tournament_id}/generate-bracket")
async def generate_bracket(
    tournament_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate tournament bracket (admin only)"""
    try:
        bracket = TournamentService.generate_bracket(db, tournament_id)
        return {
            "success": True,
            "data": {"bracket": bracket}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my/tournaments")
async def get_my_tournaments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's registered tournaments"""
    registrations = db.query(TournamentRegistration).filter(
        TournamentRegistration.user_id == current_user.id
    ).all()
    
    return {
        "success": True,
        "data": {
            "registrations": [r.to_dict() for r in registrations]
        }
    }
