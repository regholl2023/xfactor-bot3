"""
Admin authentication for the trading bot.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from loguru import logger


# Security configuration
ADMIN_PASSWORD_HASH = hashlib.sha256("106431".encode()).hexdigest()
TOKEN_EXPIRY_HOURS = 24

# Active sessions
_active_sessions: dict[str, datetime] = {}

security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Login request model."""
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    token: Optional[str] = None
    expires_at: Optional[str] = None
    message: str = ""


class AdminUser(BaseModel):
    """Authenticated admin user."""
    token: str
    authenticated_at: datetime


def verify_password(password: str) -> bool:
    """Verify admin password."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return secrets.compare_digest(password_hash, ADMIN_PASSWORD_HASH)


def create_session_token() -> tuple[str, datetime]:
    """Create a new session token."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    _active_sessions[token] = expires_at
    return token, expires_at


def validate_token(token: str) -> bool:
    """Validate a session token."""
    if token not in _active_sessions:
        return False
    
    expires_at = _active_sessions[token]
    if datetime.utcnow() > expires_at:
        del _active_sessions[token]
        return False
    
    return True


def revoke_token(token: str) -> bool:
    """Revoke a session token."""
    if token in _active_sessions:
        del _active_sessions[token]
        return True
    return False


def cleanup_expired_sessions() -> int:
    """Clean up expired sessions."""
    now = datetime.utcnow()
    expired = [token for token, expires in _active_sessions.items() if now > expires]
    for token in expired:
        del _active_sessions[token]
    return len(expired)


async def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> AdminUser:
    """
    Dependency to verify admin authentication.
    
    Usage:
        @router.get("/admin/something")
        async def admin_route(admin: AdminUser = Depends(get_admin_user)):
            ...
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    if not validate_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AdminUser(
        token=token,
        authenticated_at=datetime.utcnow(),
    )


async def optional_admin_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[AdminUser]:
    """
    Optional admin authentication - returns None if not authenticated.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    if not validate_token(token):
        return None
    
    return AdminUser(
        token=token,
        authenticated_at=datetime.utcnow(),
    )

