from fastapi import Response
from ..auth import ENVIRONMENT, COOKIE_DOMAIN


def set_auth_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int,
    path: str = "/",
) -> None:
    """Set an authentication cookie with secure defaults."""
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
        domain=COOKIE_DOMAIN,
        max_age=max_age,
        path=path,
    )


def delete_auth_cookie(response: Response, key: str, path: str = "/") -> None:
    """Delete an authentication cookie with matching security settings."""
    response.delete_cookie(
        key=key,
        path=path,
        domain=COOKIE_DOMAIN,
        httponly=True,
        secure=ENVIRONMENT == "production",
        samesite="lax",
    )