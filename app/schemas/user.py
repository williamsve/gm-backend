from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Esquemas para request
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Esquemas para response
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema para solicitar un nuevo access token usando refresh token"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Schema para la respuesta al refrescar el token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

