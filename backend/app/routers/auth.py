from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import random
import logging
import os

from ..auth import (
    GoogleOAuthError,
    exchange_code_for_token,
    get_user_info,
    create_tokens,
    refresh_access_token,
    revoke_refresh_token,
    get_google_auth_url,
    FRONTEND_URL,
    ENVIRONMENT,
    COOKIE_DOMAIN,
    verify_jwt_token,
    create_guest_tokens,
    refresh_guest_access_token,
)
from ..models import (
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    UpdateUsernameRequest,
)
from ..database import get_db_session
from ..svc.database_service import DatabaseService

router = APIRouter(prefix="/auth", tags=["authentication"])

# Rate limiter will be set from main.py
limiter = None


def get_limiter():
    """Get the limiter instance, creating a default one if needed"""
    global limiter
    if limiter is None:
        from slowapi import Limiter
        from slowapi.util import get_remote_address

        limiter = Limiter(key_func=get_remote_address)
    return limiter


async def generate_unique_username(db_service: DatabaseService) -> str:
    """Generate a unique username in format user_12345678"""
    max_attempts = 10
    for _ in range(max_attempts):
        # Generate 8 random digits
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
        username = f"user_{random_digits}"

        # Check if username already exists
        existing_user = await db_service.get_user_by_username(username)
        if not existing_user:
            return username

    # Fallback if we couldn't generate a unique username after max_attempts
    import time

    timestamp = str(int(time.time()))[-8:]  # Use last 8 digits of timestamp
    return f"user_{timestamp}"


async def get_or_create_user(user_info: dict, db_service: DatabaseService) -> dict:
    """Get existing user or create new user from Google OAuth info"""
    # Check if user already exists
    existing_user = await db_service.get_user_by_id(user_info["id"])

    if existing_user:
        # Return existing user data
        return {
            "id": existing_user.id,
            "email": existing_user.email,
            "name": existing_user.name,
            "username": existing_user.username,
        }

    # Create new user
    username = await generate_unique_username(db_service)
    user_data = {
        "id": user_info["id"],
        "email": user_info["email"],
        "name": user_info["name"],
        "username": username,
        "user_type": "authenticated",
    }

    new_user = await db_service.create_user(user_data)
    return {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "username": new_user.username,
    }


@router.get("/google")
@get_limiter().limit("10/minute")
async def google_auth(request: Request):
    """Initiate Google OAuth flow"""
    try:
        auth_url = get_google_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Google auth URL: {str(e)}"
        )


@router.get("/callback")
@get_limiter().limit("10/minute")
async def auth_callback(
    request: Request,
    code: Optional[str] = Query(None, description="Authorization code from Google"),
    error: Optional[str] = Query(None, description="Error from Google OAuth"),
    state: Optional[str] = Query(None, description="State parameter"),
    db_session: AsyncSession = Depends(get_db_session),
):
    """Handle Google OAuth callback"""

    # Check for OAuth errors
    if error:
        error_msg = f"Google OAuth error: {error}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)

    # Check for missing authorization code
    if not code:
        error_msg = "Missing authorization code"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)

    try:
        auth_result = await _process_oauth_callback(code, db_session)
        redirect_url = f"{FRONTEND_URL}/auth/success"
        return _create_auth_response(
            redirect_url, auth_result["access_token"], auth_result["refresh_token"]
        )

    except GoogleOAuthError as e:
        error_msg = f"OAuth authentication failed: {str(e)}"
        return _create_error_response(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        return _create_error_response(error_msg)


@router.get("/me", response_model=UserResponse)
@get_limiter().limit("60/minute")
async def get_current_user(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
):
    """Get current user information from database, with automatic token refresh and guest session fallback"""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    refresh_token_value = request.cookies.get("refresh_token")

    # Try to validate access token first
    payload = None
    if access_token:
        payload = verify_jwt_token(access_token)

    # If access token is invalid or missing, try to refresh
    if not payload and refresh_token_value:
        # Try to refresh the token
        new_access_token = None

        if refresh_token_value.startswith("guest_refresh_"):
            # Handle guest refresh tokens
            new_access_token = await refresh_guest_access_token(refresh_token_value)
        else:
            # Handle authenticated user refresh tokens
            new_access_token = await refresh_access_token(refresh_token_value)

        if new_access_token:
            # Successfully refreshed, verify new token
            payload = verify_jwt_token(new_access_token)
            if payload:
                # Create response with refreshed user data
                db_service = DatabaseService(db_session)
                user = await db_service.get_user_by_id(payload["sub"])

                if user:
                    response = JSONResponse(
                        content={
                            "id": user.id,
                            "email": user.email if user.email else "",
                            "name": user.name,
                            "user_type": user.user_type,
                            "username": user.username,
                        }
                    )
                    # Set new access token cookie
                    response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        secure=ENVIRONMENT == "production",
                        samesite="lax",
                        domain=COOKIE_DOMAIN,
                        max_age=3600,  # 1 hour
                        path="/",
                    )
                    return response

    # If we still don't have a valid token, create guest session as fallback
    if not payload:
        # Create new guest session
        guest_access_token, guest_refresh_token = create_guest_tokens()

        token_payload = verify_jwt_token(guest_access_token)
        if token_payload and token_payload.get("user_type") == "guest":
            guest_id = token_payload["sub"]
            guest_name = token_payload.get("name", "Guest")

            # Store guest user in database
            try:
                db_service = DatabaseService(db_session)
                existing_user = await db_service.get_user_by_id(guest_id)
                if not existing_user:
                    await db_service.create_guest_user(guest_id, guest_name)

                # Get the created/existing guest user
                user = await db_service.get_user_by_id(guest_id)
                if user:
                    response = JSONResponse(
                        content={
                            "id": user.id,
                            "email": user.email if user.email else "",
                            "name": user.name,
                            "user_type": user.user_type,
                            "username": user.username,
                        }
                    )

                    # Set guest access token cookie
                    response.set_cookie(
                        key="access_token",
                        value=guest_access_token,
                        httponly=True,
                        secure=ENVIRONMENT == "production",
                        samesite="lax",
                        domain=COOKIE_DOMAIN,
                        max_age=3600,  # 1 hour
                        path="/",
                    )

                    # Set guest refresh token cookie
                    response.set_cookie(
                        key="refresh_token",
                        value=guest_refresh_token,
                        httponly=True,
                        secure=ENVIRONMENT == "production",
                        samesite="lax",
                        domain=COOKIE_DOMAIN,
                        max_age=7 * 24 * 60 * 60,  # 7 days
                        path="/",
                    )

                    return response
            except Exception as e:
                logging.error(f"Failed to create guest session in /me endpoint: {e}")

    # If we have a valid payload, get user from database
    if payload:
        db_service = DatabaseService(db_session)
        user = await db_service.get_user_by_id(payload["sub"])

        if not user:
            # Clear cookies when user not found
            response = JSONResponse(
                content={"detail": "User not found in database"}, status_code=404
            )
            response.delete_cookie(
                key="access_token",
                path="/",
                httponly=True,
                secure=ENVIRONMENT == "production",
                samesite="lax",
            )
            response.delete_cookie(
                key="refresh_token",
                path="/",
                httponly=True,
                secure=ENVIRONMENT == "production",
                samesite="lax",
            )
            return response

        return UserResponse(
            id=user.id,
            email=user.email if user.email else "",
            name=user.name,
            user_type=user.user_type,
            username=user.username,
        )

    # Final fallback - clear cookies and return unauthorized
    response = JSONResponse(
        content={"detail": "Unable to authenticate user"}, status_code=401
    )
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
    )
    return response


@router.get("/ws-token")
@get_limiter().limit("10/minute")
async def get_websocket_token(request: Request):
    """Get access token for WebSocket connections"""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    # Verify the token is valid
    payload = verify_jwt_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"access_token": access_token}


@router.post("/logout")
@get_limiter().limit("10/minute")
async def logout(request: Request, refresh_request: RefreshTokenRequest = None):
    """Logout user by revoking refresh token"""

    # Try to get refresh token from request body first, then from cookie
    refresh_token_value = None

    if refresh_request and refresh_request.refresh_token:
        refresh_token_value = refresh_request.refresh_token
    else:
        # Try to get from cookie
        refresh_token_value = request.cookies.get("refresh_token")

    # Try to revoke the refresh token if it exists, but don't fail if it doesn't
    if refresh_token_value:
        await revoke_refresh_token(refresh_token_value)

    response = JSONResponse(content={"message": "Successfully logged out"})

    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
    )

    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
    )

    return response


@router.patch("/me/username", response_model=UserResponse)
@get_limiter().limit("10/minute")
async def update_usernamename(
    request: Request,
    update_request: UpdateUsernameRequest,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Update current user's username (stored in username field)"""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = verify_jwt_token(access_token)
    if not payload:
        response = JSONResponse(
            content={"detail": "Invalid or expired token"}, status_code=401
        )
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            secure=ENVIRONMENT == "production",
            samesite="lax",
        )
        response.delete_cookie(
            key="refresh_token",
            path="/",
            httponly=True,
            secure=ENVIRONMENT == "production",
            samesite="lax",
        )
        return response

    # Check if user is a guest - guests cannot change their username
    if payload.get("user_type") == "guest":
        raise HTTPException(
            status_code=403, detail="Guest users cannot change their username"
        )

    db_service = DatabaseService(db_session)
    user = await db_service.update_user_username(
        payload["sub"], update_request.username
    )

    if not user:
        # Check if user exists at all
        existing_user = await db_service.get_user_by_id(payload["sub"])
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=400, detail="Username already taken")

    return UserResponse(
        id=user.id,
        email=user.email if user.email else "",
        name=user.name,
        user_type=user.user_type,
        username=user.username,
    )


# Helper methods for authentication flows
async def _process_oauth_callback(code: str, db_session: AsyncSession):
    """Process OAuth callback by exchanging code for token and getting user info."""
    # Exchange authorization code for access token
    token_data = await exchange_code_for_token(code)

    # Get user information from Google
    user_info = await get_user_info(token_data["access_token"])

    # Get or create user in database
    db_service = DatabaseService(db_session)
    user_data = await get_or_create_user(user_info, db_service)

    # Create both access and refresh tokens for our application
    access_token, refresh_token = await create_tokens(user_info, token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_data": user_data,
        "user_info": user_info,
    }


def _create_auth_response(redirect_url: str, access_token: str, refresh_token: str):
    """Create authentication response with proper cookie settings."""
    response = RedirectResponse(url=redirect_url, status_code=302)

    # Set access token as an HTTP-only secure cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=os.getenv("ENVIRONMENT")
        == "production",  # Only send over HTTPS in production
        samesite="lax",  # Better CSRF protection
        domain=COOKIE_DOMAIN,
        max_age=3600,  # 1 hour in seconds
        path="/",  # Cookie available for entire domain
    )

    # Set refresh token as an HTTP-only secure cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=os.getenv("ENVIRONMENT")
        == "production",  # Only send over HTTPS in production
        samesite="lax",  # Better CSRF protection
        domain=COOKIE_DOMAIN,
        max_age=30 * 24 * 60 * 60,  # 30 days in seconds
        path="/",  # Cookie available for entire domain
    )

    return response


def _create_error_response(error_message: str):
    """Create error response with redirect to frontend error page."""
    redirect_url = f"{FRONTEND_URL}/auth/error?message={error_message}"
    return RedirectResponse(url=redirect_url, status_code=302)
