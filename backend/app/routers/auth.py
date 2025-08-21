from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import random

from ..auth import (
    GoogleOAuthError,
    exchange_code_for_token,
    get_user_info,
    create_tokens,
    refresh_access_token,
    revoke_refresh_token,
    get_google_auth_url,
    FRONTEND_URL,
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
    }

    new_user = await db_service.create_user(user_data)
    return {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "username": new_user.username,
    }


@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        auth_url = get_google_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Google auth URL: {str(e)}"
        )


@router.get("/callback")
async def auth_callback(
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
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(code)

        # Get user information from Google
        user_info = await get_user_info(token_data["access_token"])

        # Get or create user in database
        db_service = DatabaseService(db_session)
        await get_or_create_user(user_info, db_service)

        # Create both access and refresh tokens for our application
        access_token, refresh_token = await create_tokens(user_info, token_data)

        # Redirect to frontend without access token in URL
        redirect_url = f"{FRONTEND_URL}/auth/success"

        response = RedirectResponse(url=redirect_url, status_code=302)

        # Set access token as an HTTP-only secure cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=True,  # Only send over HTTPS in production
            samesite="strict",  # CSRF protection
            max_age=3600,  # 1 hour in seconds
            path="/",  # Cookie available for entire domain
        )

        # Set refresh token as an HTTP-only secure cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=True,  # Only send over HTTPS in production
            samesite="strict",  # CSRF protection
            max_age=30 * 24 * 60 * 60,  # 30 days in seconds
            path="/",  # Cookie available for entire domain
        )

        return response

    except GoogleOAuthError as e:
        error_msg = f"OAuth authentication failed: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/token", response_model=TokenResponse)
async def get_token_from_code(
    authorization_code: str,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Exchange authorization code for tokens (JSON response)"""

    try:
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(authorization_code)

        # Get user information from Google
        user_info = await get_user_info(token_data["access_token"])

        # Get or create user in database
        db_service = DatabaseService(db_session)
        user_data = await get_or_create_user(user_info, db_service)

        # Create both access and refresh tokens for our application
        access_token, refresh_token = await create_tokens(user_info, token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour in seconds
            user=UserResponse(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                user_type="authenticated",
                username=user_data["username"],
            ),
        )

    except GoogleOAuthError as e:
        raise HTTPException(
            status_code=400, detail=f"OAuth authentication failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error during authentication: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
):
    """Get current user information from database"""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = verify_jwt_token(access_token)
    if not payload:
        # Clear cookies when access token is invalid
        response = JSONResponse(
            content={"detail": "Invalid or expired token"}, status_code=401
        )
        response.delete_cookie(
            key="access_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        response.delete_cookie(
            key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        return response

    db_service = DatabaseService(db_session)
    user = await db_service.get_user_by_id(payload["sub"])

    if not user:
        response = JSONResponse(
            content={"detail": "User not found in database"}, status_code=404
        )
        response.delete_cookie(
            key="access_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        response.delete_cookie(
            key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        return response

    return UserResponse(
        id=user.id,
        email=user.email if user.email else "",
        name=user.name,
        user_type=user.user_type,
        username=user.username,
    )


@router.post("/refresh")
async def refresh_token(request: Request, refresh_request: RefreshTokenRequest = None):
    """Refresh access token using refresh token"""

    # Try to get refresh token from cookie first, then from request body
    refresh_token_value = None

    if refresh_request and refresh_request.refresh_token:
        refresh_token_value = refresh_request.refresh_token
    else:
        # Try to get from cookie
        refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="Refresh token not provided")

    # Handle guest refresh tokens
    if refresh_token_value.startswith("guest_refresh_"):
        new_access_token = await refresh_guest_access_token(refresh_token_value)
        if not new_access_token:
            response = JSONResponse(
                content={"detail": "Invalid or expired guest refresh token"},
                status_code=401,
            )
            response.delete_cookie(
                key="refresh_token",
                path="/",
                httponly=True,
                secure=True,
                samesite="strict",
            )
            return response
    else:
        # Handle authenticated user refresh tokens (existing logic)
        new_access_token = await refresh_access_token(refresh_token_value)
        if not new_access_token:
            # Clear the invalid refresh token cookie
            response = JSONResponse(
                content={"detail": "Invalid or expired refresh token"}, status_code=401
            )
            response.delete_cookie(
                key="refresh_token",
                path="/",
                httponly=True,
                secure=True,
                samesite="strict",
            )
            return response

    # Return success message and set new access token in cookie
    response = JSONResponse(content={"message": "Token refreshed successfully"})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=True,  # Only send over HTTPS in production
        samesite="strict",  # CSRF protection
        max_age=3600,  # 1 hour in seconds
        path="/",  # Cookie available for entire domain
    )

    return response


@router.get("/ws-token")
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
        key="access_token", path="/", httponly=True, secure=True, samesite="strict"
    )

    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
    )

    return response


@router.post("/guest-session")
async def create_guest_session(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
):
    """Create or reuse guest session with refresh token and store guest user in database"""

    # Check for existing refresh token first - prioritize reuse over creation
    existing_refresh_token = request.cookies.get("refresh_token")

    if existing_refresh_token and existing_refresh_token.startswith("guest_refresh_"):
        # Try to refresh the existing guest session
        try:
            new_access_token = await refresh_guest_access_token(existing_refresh_token)
            if new_access_token:
                # Existing session is valid, return refreshed access token (no DB operations needed)
                response = JSONResponse(
                    content={"message": "Guest session refreshed", "user_type": "guest"}
                )

                # Set refreshed access token cookie
                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    secure=True,
                    samesite="strict",
                    max_age=3600,  # 1 hour
                    path="/",
                )

                return response
        except Exception as e:
            print(f"Failed to refresh existing guest session: {e}")
            # Continue to create new session below

    # Create new guest session only if no existing valid session found
    guest_access_token, guest_refresh_token = create_guest_tokens()

    token_payload = verify_jwt_token(guest_access_token)
    if token_payload and token_payload.get("user_type") == "guest":
        guest_id = token_payload["sub"]
        guest_name = token_payload.get("name", "Guest")

        # Store guest user in database
        try:
            db_service = DatabaseService(db_session)
            # Check if guest user already exists
            existing_user = await db_service.get_user_by_id(guest_id)
            if not existing_user:
                await db_service.create_guest_user(guest_id, guest_name)
        except Exception as e:
            print(f"Failed to store guest user {guest_id}: {e}")

    response = JSONResponse(
        content={"message": "Guest session created", "user_type": "guest"}
    )

    # Set guest access token cookie
    response.set_cookie(
        key="access_token",
        value=guest_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=3600,  # 1 hour
        path="/",
    )

    # Set guest refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=guest_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )

    return response


@router.patch("/me/username", response_model=UserResponse)
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
            key="access_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        response.delete_cookie(
            key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        return response

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
