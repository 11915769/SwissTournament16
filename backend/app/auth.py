import json
import os
import firebase_admin
from firebase_admin import auth as fb_auth, credentials
from fastapi import Header, HTTPException

_initialized = False

def init_firebase():
    global _initialized
    if _initialized:
        return

    # Option 1: JSON in env (recommended for Railway)
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        data = json.loads(sa_json)
        cred = credentials.Certificate(data)  # accepts dict
        firebase_admin.initialize_app(cred)
        _initialized = True
        return

    # Option 2: file path (useful for local Docker with a mounted file)
    path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH")
    if not path:
        raise RuntimeError("Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH")
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
    _initialized = True

async def get_current_user(authorization: str | None = Header(default=None)):
    init_firebase()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    try:
        decoded = fb_auth.verify_id_token(token)
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
            "name": decoded.get("name"),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")