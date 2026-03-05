import os
from fastapi import Depends, HTTPException, Request
from app.auth import get_current_user


def _parse_admin_emails() -> set[str]:
    raw = os.environ.get("ADMIN_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


async def require_user(request: Request, user=Depends(get_current_user)):
    # ✅ Allow CORS preflight requests through (no auth headers on OPTIONS)
    if request.method == "OPTIONS":
        return None
    return user


async def require_admin(request: Request, user=Depends(get_current_user)):
    # ✅ Allow CORS preflight requests through (no auth headers on OPTIONS)
    if request.method == "OPTIONS":
        return None

    admins = _parse_admin_emails()
    email = (user.get("email") or "").lower()

    if not admins:
        raise HTTPException(status_code=500, detail="ADMIN_EMAILS is not configured")

    if email not in admins:
        raise HTTPException(status_code=403, detail="Admin only")

    return user