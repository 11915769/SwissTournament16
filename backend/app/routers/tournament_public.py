from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from app.constants import TOURNAMENT_ID
from app.db import get_db
from app.deps import require_user
from app.swiss import compute_standings
from pydantic import BaseModel

router = APIRouter(prefix="/tournament", tags=["tournament"])

class JoinRequest(BaseModel):
    name: str

@router.get("/state")
async def state(user=Depends(require_user)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    players = [p.to_dict() for p in t_ref.collection("players").stream()]
    players.sort(key=lambda x: x.get("joinedAt", ""))

    # include current matches depending on stage
    current_matches = []
    bracket_matches = []

    status = t.get("status")

    if status == "swiss":
        cur = int(t.get("currentRound", 0))
        current_matches = [
            m.to_dict() for m in t_ref.collection("matches")
            .where("stage", "==", "swiss")
            .where("round", "==", cur)
            .stream()
        ]
        current_matches.sort(key=lambda m: (m.get("p1Uid", ""), m.get("p2Uid", "")))

    elif status in ("top8", "done"):
        # load all bracket matches
        bracket_matches = [
            m.to_dict() for m in t_ref.collection("matches")
            .where("stage", "==", "bracket")
            .stream()
        ]

        # "current" = playable matches (both players set, winner not set)
        current_matches = bracket_matches

        # nice ordering if you have round/code fields
        bracket_matches.sort(key=lambda m: (m.get("round", 0), m.get("code", ""), m.get("id", "")))
        current_matches.sort(key=lambda m: (m.get("round", 0), m.get("code", ""), m.get("id", "")))

    return {
        "tournament": t,
        "players": players,
        "playerCount": len(players),
        "currentMatches": current_matches,
        "bracketMatches": bracket_matches,  # optional but very useful
    }

@router.post("/join")
async def join(data: JoinRequest, user=Depends(require_user)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    if t.get("status") != "registration":
        raise HTTPException(400, "Registration is closed")

    players_ref = t_ref.collection("players")
    if players_ref.document(user["uid"]).get().exists:
        return {"ok": True, "alreadyJoined": True}

    cap = int(t.get("playersMax", 16))
    count = sum(1 for _ in players_ref.stream())
    if count >= cap:
        raise HTTPException(400, "Tournament is full")

    players_ref.document(user["uid"]).set({
        "uid": user["uid"],
        "email": user.get("email"),
        "name": data.name,
    }, merge=True)

    return {"ok": True, "alreadyJoined": False}

@router.get("/standings")
async def standings(user=Depends(require_user)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    players = [p.to_dict() for p in t_ref.collection("players").stream()]
    player_uids = [p["uid"] for p in players if p.get("uid")]

    matches = [m.to_dict() for m in t_ref.collection("matches").where("stage", "==", "swiss").stream()]
    recs = compute_standings(player_uids, matches)

    # map uid -> email for display
    email_by_uid = {p["uid"]: p.get("email") for p in players if p.get("uid")}
    name_by_uid = {p["uid"]: p.get("name") for p in players if p.get("uid")}

    return {
        "tournament": {"status": t.get("status"), "currentRound": t.get("currentRound")},
        "standings": [
            {
                "uid": r.uid,
                "email": email_by_uid.get(r.uid),
                "name": name_by_uid.get(r.uid),
                "wins": r.wins,
                "losses": r.losses,
                "buchholz": r.buchholz,
            }
            for r in recs
        ]
    }