from pydantic import BaseModel, field_validator
from typing import Optional
import re


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    user_type: Optional[str] = "authenticated"
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateUsernameRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")

        v = v.strip()

        if len(v) > 16:
            raise ValueError("Username cannot exceed 16 characters")

        if len(v) < 1:
            raise ValueError("Username must be at least 1 character")

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return v
