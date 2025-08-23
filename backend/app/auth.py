import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import httpx
from jose import JWTError, jwt
from dotenv import load_dotenv
import secrets
import time
import random
from uuid import uuid4
from app.database import get_db_session
from app.svc.database_service import DatabaseService

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
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "http://localhost:3000")

# Google OAuth URLs
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


# In-memory storage for guest refresh tokens
guest_refresh_tokens: dict[str, dict] = {}


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


async def refresh_google_token(google_refresh_token: str) -> dict:
    """Refresh Google access token using Google's refresh token"""
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": google_refresh_token,
            "grant_type": "refresh_token",
        }

        response = await client.post(GOOGLE_TOKEN_URL, data=data)

        if response.status_code != 200:
            raise GoogleOAuthError(f"Failed to refresh Google token: {response.text}")

        return response.json()


async def create_tokens(
    user_data: dict, google_token_data: dict = None
) -> Tuple[str, str]:
    """Create both access and refresh tokens for authenticated user"""
    # Create access token with shorter expiry
    access_expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    access_payload = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "exp": access_expire,
        "type": "access",
    }
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Create refresh token with longer expiry
    refresh_expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRATION_DAYS
    )
    refresh_token = secrets.token_urlsafe(32)

    # Store refresh token in database
    async for session in get_db_session():
        db_service = DatabaseService(session)
        token_data = {
            "token": refresh_token,
            "user_id": user_data["id"],
            "expires_at": refresh_expire.replace(tzinfo=None),
            "google_refresh_token": google_token_data.get("refresh_token")
            if google_token_data
            else None,
            "google_token_expires_at": (
                datetime.now(timezone.utc)
                + timedelta(seconds=google_token_data.get("expires_in", 3600 * 24 * 7))
            ).replace(tzinfo=None)
            if google_token_data
            else None,
        }
        await db_service.create_refresh_token(token_data)
        break

    return access_token, refresh_token


async def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Create a new access token using a valid refresh token"""
    async for session in get_db_session():
        db_service = DatabaseService(session)
        token_obj = await db_service.get_refresh_token(refresh_token)

        if not token_obj:
            return None

        # Check if refresh token is expired
        if datetime.now(timezone.utc).replace(tzinfo=None) > token_obj.expires_at:
            # Clean up expired token
            await db_service.delete_refresh_token(token_obj)
            return None

        try:
            # Check if we have a Google refresh token and if Google token is expired
            google_refresh_token = token_obj.google_refresh_token
            google_token_expires_at = token_obj.google_token_expires_at

            if (
                google_refresh_token
                and google_token_expires_at
                and datetime.now(timezone.utc).replace(tzinfo=None)
                > google_token_expires_at
            ):
                # Refresh Google token
                refreshed_google_token = await refresh_google_token(
                    google_refresh_token
                )

                # Update stored Google token expiration
                token_obj.google_token_expires_at = (
                    datetime.now(timezone.utc)
                    + timedelta(seconds=refreshed_google_token.get("expires_in", 3600))
                ).replace(tzinfo=None)
                await db_service.update_refresh_token(token_obj)

                # Get fresh user info from Google
                user_data = await get_user_info(refreshed_google_token["access_token"])
            else:
                # Get user data from database if Google token is still valid
                user = await db_service.get_user_by_id(token_obj.user_id)
                if not user:
                    return None
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                }

            # Create new access token (just the JWT, don't create new refresh token)
            access_expire = datetime.now(timezone.utc) + timedelta(
                hours=JWT_EXPIRATION_HOURS
            )
            access_payload = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "exp": access_expire,
                "type": "access",
            }
            access_token = jwt.encode(
                access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
            )
            return access_token

        except GoogleOAuthError:
            # If Google token refresh fails, fall back to user data from database
            user = await db_service.get_user_by_id(token_obj.user_id)
            if not user:
                return None
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
            }
            access_expire = datetime.now(timezone.utc) + timedelta(
                hours=JWT_EXPIRATION_HOURS
            )
            access_payload = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "exp": access_expire,
                "type": "access",
            }
            access_token = jwt.encode(
                access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
            )
            return access_token


async def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a refresh token"""
    async for session in get_db_session():
        db_service = DatabaseService(session)
        token_obj = await db_service.get_refresh_token(refresh_token)

        if token_obj:
            await db_service.delete_refresh_token(token_obj)
            return True
        return False


async def cleanup_expired_refresh_tokens():
    """Remove expired refresh tokens from storage"""
    async for session in get_db_session():
        db_service = DatabaseService(session)
        return await db_service.cleanup_expired_refresh_tokens()


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


def create_jwt_token(payload: dict, expires_minutes: int = 60) -> str:
    """Create JWT token with given payload and expiration"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload_copy = payload.copy()
    payload_copy.update({"exp": expire, "type": "access"})
    return jwt.encode(payload_copy, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_guest_tokens(guest_name: str = None) -> Tuple[str, str]:
    """Create guest access and refresh tokens"""
    guest_id = "guest_" + str(uuid4())
    guest_name = guest_name or f"Guest_{random.randint(10000, 99999)}"

    # Create guest access token (JWT)
    guest_access_token = create_jwt_token(
        {
            "sub": guest_id,
            "email": "guest@local",
            "name": guest_name,
            "user_type": "guest",
        },
        expires_minutes=60,
    )

    # Create guest refresh token
    guest_refresh_token = "guest_refresh_" + secrets.token_urlsafe(32)

    # Store guest session
    guest_refresh_tokens[guest_refresh_token] = {
        "guest_id": guest_id,
        "guest_name": guest_name,
        "created_at": time.time(),
        "last_used": time.time(),
        "expires_at": time.time() + (7 * 24 * 60 * 60),  # 7 days
    }

    return guest_access_token, guest_refresh_token


async def refresh_guest_access_token(guest_refresh_token: str) -> Optional[str]:
    """Refresh guest access token using guest refresh token"""
    if not guest_refresh_token.startswith("guest_refresh_"):
        return None

    if guest_refresh_token not in guest_refresh_tokens:
        return None

    token_data = guest_refresh_tokens[guest_refresh_token]

    # Check expiry
    if time.time() > token_data["expires_at"]:
        del guest_refresh_tokens[guest_refresh_token]
        return None

    # Update last used
    token_data["last_used"] = time.time()

    # Create new access token
    return create_jwt_token(
        {
            "sub": token_data["guest_id"],
            "email": "guest@local",
            "name": token_data["guest_name"],
            "user_type": "guest",
        },
        expires_minutes=60,
    )


def cleanup_expired_guest_tokens():
    """Remove expired guest tokens"""
    current_time = time.time()
    expired_tokens = [
        token
        for token, data in guest_refresh_tokens.items()
        if current_time > data["expires_at"]
    ]
    for token in expired_tokens:
        del guest_refresh_tokens[token]

    return len(expired_tokens)
