from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.deps import require_admin
from app.db import get_db
from app.constants import TOURNAMENT_ID

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/create-tournament")
async def create_tournament(admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)

    # Idempotent: don't overwrite if it already exists
    existing = t_ref.get()
    if existing.exists:
        return {"created": False, "tournamentId": TOURNAMENT_ID}

    t_ref.set({
        "name": "Kniffel Swiss Tournament",
        "playersMax": 16,
        "swissRounds": 5,
        "status": "registration",
        "currentRound": 0,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "createdByUid": admin["uid"],
        "createdByEmail": admin.get("email"),
    })

    return {"created": True, "tournamentId": TOURNAMENT_ID}


@router.post("/delete-tournament")
async def delete_tournament(admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        return {"ok": True, "deleted": False, "reason": "not_found"}

    # delete players subcollection docs
    for doc in t_ref.collection("players").stream():
        doc.reference.delete()

    # delete matches subcollection docs
    for doc in t_ref.collection("matches").stream():
        doc.reference.delete()

    # delete tournament doc
    t_ref.delete()

    return {"ok": True, "deleted": True}

@router.post("/reset-tournament")
async def reset_tournament(admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)

    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")

    t = t_doc.to_dict() or {}

    # keep tournament config if present
    name = t.get("name", "Kniffel Swiss Tournament")
    players_max = int(t.get("playersMax", 16))
    swiss_rounds = int(t.get("swissRounds", 5))

    now = datetime.now(timezone.utc).isoformat()

    # Snapshot current registered players (keep only safe identity fields)
    players_snap = []
    for p in t_ref.collection("players").stream():
        d = p.to_dict() or {}
        uid = d.get("uid") or p.id
        if not uid:
            continue
        players_snap.append({
            "uid": uid,
            "name": d.get("name"),
            "email": d.get("email"),
        })

    # Delete all matches
    for m in t_ref.collection("matches").stream():
        m.reference.delete()

    # Delete all players (we'll recreate clean)
    for p in t_ref.collection("players").stream():
        p.reference.delete()

    # Overwrite tournament doc completely (NO merge) to wipe any stale fields
    t_ref.set({
        "name": name,
        "playersMax": players_max,
        "swissRounds": swiss_rounds,
        "status": "registration",
        "currentRound": 0,
        "createdAt": t.get("createdAt", now),
        "resetAt": now,
        "resetByUid": admin.get("uid"),
        "resetByEmail": admin.get("email"),
    }, merge=False)

    # Recreate players with a clean schema
    for p in players_snap:
        t_ref.collection("players").document(p["uid"]).set({
            "uid": p["uid"],
            "name": p.get("name"),
            "email": p.get("email"),
            "registeredAt": now,
        }, merge=False)

    return {"ok": True, "playersRestored": len(players_snap)}

@router.post("/players/{uid}/remove")
async def remove_player(uid: str, user=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")

    t = t_doc.to_dict() or {}
    if t.get("status") != "registration":
        raise HTTPException(400, "You can only remove players during registration")

    players_ref = t_ref.collection("players")
    p_doc = players_ref.document(uid).get()
    if not p_doc.exists:
        raise HTTPException(404, "Player not found")

    players_ref.document(uid).delete()
    return {"ok": True}