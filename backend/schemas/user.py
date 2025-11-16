"""
User Profile Schemas
Pydantic models for user profile requests/responses
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime, date


# Request Schemas
class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100, example="John Doe")
    bio: Optional[str] = Field(None, max_length=500, example="Professional gamer")
    email: Optional[EmailStr] = Field(None, example="john@example.com")
    date_of_birth: Optional[date] = Field(None, example="1995-01-15")
    state: Optional[str] = Field(None, max_length=50, example="Maharashtra")
    city: Optional[str] = Field(None, max_length=100, example="Mumbai")
    pincode: Optional[str] = Field(None, max_length=10, example="400001")

    @validator('date_of_birth')
    def validate_age(cls, v):
        if v:
            today = datetime.now().date()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError('User must be at least 18 years old')
        return v


# Response Schemas
class GameWiseStatsResponse(BaseModel):
    """Statistics for a specific game"""
    game_code: str
    games_played: int
    games_won: int
    elo_rating: int

    class Config:
        from_attributes = True


class UserStatisticsResponse(BaseModel):
    """User gaming statistics"""
    total_games_played: int
    total_games_won: int
    total_games_lost: int
    win_percentage: float
    total_winnings: float  # in rupees
    total_spent: float  # in rupees
    net_profit: float  # in rupees
    current_streak: int
    longest_streak: int
    game_wise_stats: list[GameWiseStatsResponse] = []

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Complete user profile"""
    id: str
    username: str
    display_name: Optional[str]
    email: Optional[str]
    phone: str
    avatar_url: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    state: Optional[str]
    city: Optional[str]
    kyc_status: str
    referral_code: str
    level: int
    experience_points: int
    statistics: UserStatisticsResponse
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileResponse(BaseModel):
    """Response for profile update"""
    message: str
    profile: UserProfileResponse
