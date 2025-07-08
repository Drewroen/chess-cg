from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from typing import Optional

from .auth import (
    GoogleOAuthError,
    exchange_code_for_token,
    get_user_info,
    create_jwt_token,
    get_google_auth_url,
    FRONTEND_URL,
)
from .models import UserResponse

app = FastAPI(
    title="Chess CG API", description="A chess game backend API", version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Chess CG API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        auth_url = get_google_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Google auth URL: {str(e)}"
        )


@app.get("/auth/callback")
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

        # Create JWT token for our application
        jwt_token = create_jwt_token(user_info)

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/auth/success?token={jwt_token}"

        return RedirectResponse(url=redirect_url, status_code=302)

    except GoogleOAuthError as e:
        error_msg = f"OAuth authentication failed: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        redirect_url = f"{FRONTEND_URL}/auth/error?message={error_msg}"
        return RedirectResponse(url=redirect_url, status_code=302)


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Query(..., description="JWT token")):
    """Get current user information from JWT token"""
    from .auth import verify_jwt_token

    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return UserResponse(
        id=payload["sub"],
        email=payload["email"],
        name=payload["name"],
        picture=payload.get("picture"),
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
