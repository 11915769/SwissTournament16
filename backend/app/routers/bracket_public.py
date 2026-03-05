from __future__ import annotations
from fastapi import APIRouter, Depends
from app.constants import TOURNAMENT_ID
from app.db import get_db
from app.deps import require_user

router = APIRouter(prefix="/tournament", tags=["tournament"])

@router.get("/bracket")
async def bracket(user=Depends(require_user)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    matches = [m.to_dict() for m in t_ref.collection("matches").where("stage", "==", "bracket").stream()]

    def key(m):
        order = {"QF": 1, "SF": 2, "F": 3}
        return (order.get(m.get("bracketRound"), 99), m.get("code", ""))

    matches.sort(key=key)

    return {
        "QF": [m for m in matches if m.get("bracketRound") == "QF"],
        "SF": [m for m in matches if m.get("bracketRound") == "SF"],
        "F":  [m for m in matches if m.get("bracketRound") == "F"],
    }