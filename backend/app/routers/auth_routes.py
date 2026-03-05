from fastapi import APIRouter, Depends
from app.deps import require_user

router = APIRouter(tags=["auth"])

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/me")
async def me(user=Depends(require_user)):
    return user