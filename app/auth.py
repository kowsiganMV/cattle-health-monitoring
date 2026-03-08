"""
API key authorization dependency.
Validates the X-API-Key header on every protected request.
"""

from fastapi import Header, HTTPException
from app.config import settings


async def verify_api_key(x_api_key: str = Header(...)):
    """Reject requests with a missing or invalid API key."""
    if x_api_key != settings.API_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized request: Invalid API key",
        )
