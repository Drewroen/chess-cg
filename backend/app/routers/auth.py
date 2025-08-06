from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional

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
)
from ..models import (
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


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

        # Create both access and refresh tokens for our application
        access_token, refresh_token = create_tokens(user_info, token_data)

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
):
    """Exchange authorization code for tokens (JSON response)"""

    try:
        # Exchange authorization code for access token
        token_data = await exchange_code_for_token(authorization_code)

        # Get user information from Google
        user_info = await get_user_info(token_data["access_token"])

        # Create both access and refresh tokens for our application
        access_token, refresh_token = create_tokens(user_info, token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour in seconds
            user=UserResponse(
                id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture"),
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
async def get_current_user(request: Request):
    """Get current user information from JWT token in cookie"""

    # Get access token from cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = verify_jwt_token(access_token)
    if not payload:
        # Clear cookies when access token is invalid
        response = JSONResponse(content={"detail": "Invalid or expired token"}, status_code=401)
        response.delete_cookie(
            key="access_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        response.delete_cookie(
            key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
        )
        return response

    return UserResponse(
        id=payload["sub"],
        email=payload["email"],
        name=payload["name"],
        picture=payload.get("picture"),
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

    new_access_token = await refresh_access_token(refresh_token_value)
    if not new_access_token:
        # Clear the invalid refresh token cookie
        response = JSONResponse(content={"detail": "Invalid or expired refresh token"}, status_code=401)
        response.delete_cookie(
            key="refresh_token", path="/", httponly=True, secure=True, samesite="strict"
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
        revoke_refresh_token(refresh_token_value)

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
