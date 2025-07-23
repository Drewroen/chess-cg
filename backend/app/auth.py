import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
import httpx
from jose import JWTError, jwt
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_change_this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(
    os.getenv("JWT_EXPIRATION_HOURS", "1")
)  # Shorter access token expiry
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Google OAuth URLs
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# In-memory storage for refresh tokens (in production, use a database)
refresh_token_store: dict[str, dict] = {}


class GoogleOAuthError(Exception):
    """Custom exception for Google OAuth errors"""

    pass


async def exchange_code_for_token(authorization_code: str) -> dict:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        }

        response = await client.post(GOOGLE_TOKEN_URL, data=data)

        if response.status_code != 200:
            raise GoogleOAuthError(
                f"Failed to exchange code for token: {response.text}"
            )

        return response.json()


async def get_user_info(access_token: str) -> dict:
    """Get user information from Google"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(GOOGLE_USERINFO_URL, headers=headers)

        if response.status_code != 200:
            raise GoogleOAuthError(f"Failed to get user info: {response.text}")

        return response.json()


def create_tokens(user_data: dict) -> Tuple[str, str]:
    """Create both access and refresh tokens for authenticated user"""
    # Create access token with shorter expiry
    access_expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    access_payload = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "picture": user_data.get("picture"),
        "exp": access_expire,
        "type": "access",
    }
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Create refresh token with longer expiry
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    refresh_token = secrets.token_urlsafe(32)

    # Store refresh token with user info and expiry
    refresh_token_store[refresh_token] = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "picture": user_data.get("picture"),
        "expires_at": refresh_expire,
        "created_at": datetime.utcnow(),
    }

    return access_token, refresh_token


def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for authenticated user (backwards compatibility)"""
    access_token, _ = create_tokens(user_data)
    return access_token


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Create a new access token using a valid refresh token"""
    if refresh_token not in refresh_token_store:
        return None

    token_data = refresh_token_store[refresh_token]

    # Check if refresh token is expired
    if datetime.utcnow() > token_data["expires_at"]:
        # Clean up expired token
        del refresh_token_store[refresh_token]
        return None

    # Create new access token
    user_data = {
        "id": token_data["user_id"],
        "email": token_data["email"],
        "name": token_data["name"],
        "picture": token_data.get("picture"),
    }

    access_token, _ = create_tokens(user_data)
    return access_token


def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a refresh token"""
    if refresh_token in refresh_token_store:
        del refresh_token_store[refresh_token]
        return True
    return False


def cleanup_expired_refresh_tokens():
    """Remove expired refresh tokens from storage"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token
        for token, data in refresh_token_store.items()
        if current_time > data["expires_at"]
    ]

    for token in expired_tokens:
        del refresh_token_store[token]

    return len(expired_tokens)


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_google_auth_url() -> str:
    """Generate Google OAuth authorization URL"""
    if not GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID not configured")

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"https://accounts.google.com/o/oauth2/auth?{query_string}"
