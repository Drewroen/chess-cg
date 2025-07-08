from pydantic import BaseModel
from typing import Optional


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthCallbackResponse(BaseModel):
    success: bool
    redirect_url: str
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
