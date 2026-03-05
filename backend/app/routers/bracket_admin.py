from __future__ import annotations
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.constants import TOURNAMENT_ID
from app.db import get_db
from app.deps import require_admin
from app.swiss import compute_standings

router = APIRouter(prefix="/admin/bracket", tags=["admin-bracket"])

def _now():
    return datetime.now(timezone.utc).isoformat()

class SetWinnerBody(BaseModel):
    winnerUid: str

@router.post("/create-top8")
async def create_top8(admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    # Only allow after swiss started; ideally after round 5 complete
    if t.get("status") not in ("swiss",):
        raise HTTPException(400, f"Cannot create bracket from status={t.get('status')}")

    # Require swiss complete (currentRound == swissRounds and all those matches have winners)
    swiss_rounds = int(t.get("swissRounds", 5))
    cur = int(t.get("currentRound", 0))
    if cur < swiss_rounds:
        raise HTTPException(400, f"Swiss not complete (currentRound={cur}, swissRounds={swiss_rounds})")

    matches = [m.to_dict() for m in t_ref.collection("matches").where("stage", "==", "swiss").stream()]
    if any(int(m.get("round", 0)) == cur and not m.get("winnerUid") for m in matches):
        raise HTTPException(400, "Not all matches in final swiss round are finished")

    players = [p.to_dict() for p in t_ref.collection("players").stream()]
    player_uids = [p["uid"] for p in players if p.get("uid")]

    standings = compute_standings(player_uids, matches)
    top8 = standings[:8]
    if len(top8) < 8:
        raise HTTPException(400, "Not enough players for top 8")

    seeds = [r.uid for r in top8]  # index 0 is seed1, etc.
    pairings = [
        ("QF1", seeds[0], seeds[7]),
        ("QF2", seeds[1], seeds[6]),
        ("QF3", seeds[2], seeds[5]),
        ("QF4", seeds[3], seeds[4]),
    ]

    now = _now()
    batch = db.batch()

    # update tournament
    batch.set(t_ref, {
        "status": "top8",
        "top8Seeds": seeds,
        "bracketCreatedAt": now,
        "bracketCreatedByEmail": admin.get("email"),
    }, merge=True)

    matches_ref = t_ref.collection("matches")
    for code, p1, p2 in pairings:
        match_id = uuid.uuid4().hex
        batch.set(matches_ref.document(match_id), {
            "id": match_id,
            "stage": "bracket",
            "bracketRound": "QF",
            "code": code,
            "p1Uid": p1,
            "p2Uid": p2,
            "winnerUid": None,
            "createdAt": now,
        })

    batch.commit()
    return {"ok": True, "top8": seeds}

@router.post("/matches/{match_id}/set-winner")
async def set_bracket_winner(match_id: str, body: SetWinnerBody, admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    m_ref = t_ref.collection("matches").document(match_id)
    m_doc = m_ref.get()
    if not m_doc.exists:
        raise HTTPException(404, "Match not found")

    m = m_doc.to_dict() or {}
    if m.get("stage") != "bracket":
        raise HTTPException(400, "Not a bracket match")

    winner = body.winnerUid
    if winner not in (m.get("p1Uid"), m.get("p2Uid")):
        raise HTTPException(400, "winnerUid must be one of the two players")

    m_ref.set({
        "winnerUid": winner,
        "updatedAt": _now(),
        "updatedByEmail": admin.get("email"),
    }, merge=True)

    return {"ok": True}

@router.post("/advance")
async def advance(admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    if t.get("status") != "top8":
        raise HTTPException(400, f"Cannot advance bracket from status={t.get('status')}")

    all_bracket = [m.to_dict() for m in t_ref.collection("matches").where("stage", "==", "bracket").stream()]
    qfs = [m for m in all_bracket if m.get("bracketRound") == "QF"]
    sfs = [m for m in all_bracket if m.get("bracketRound") == "SF"]
    fs  = [m for m in all_bracket if m.get("bracketRound") == "F"]

    now = _now()
    batch = db.batch()
    matches_ref = t_ref.collection("matches")

    def all_done(ms): return ms and all(m.get("winnerUid") for m in ms)

    # Create SF if QF done and SF not created
    if qfs and all_done(qfs) and not sfs:
        w = {m["code"]: m["winnerUid"] for m in qfs}
        sf_pairings = [
            ("SF1", w["QF1"], w["QF2"]),
            ("SF2", w["QF3"], w["QF4"]),
        ]
        for code, p1, p2 in sf_pairings:
            match_id = uuid.uuid4().hex
            batch.set(matches_ref.document(match_id), {
                "id": match_id,
                "stage": "bracket",
                "bracketRound": "SF",
                "code": code,
                "p1Uid": p1,
                "p2Uid": p2,
                "winnerUid": None,
                "createdAt": now,
            })
        batch.commit()
        return {"ok": True, "created": "SF"}

    # Create Final if SF done and Final not created
    if sfs and all_done(sfs) and not fs:
        w = {m["code"]: m["winnerUid"] for m in sfs}
        match_id = uuid.uuid4().hex
        batch.set(matches_ref.document(match_id), {
            "id": match_id,
            "stage": "bracket",
            "bracketRound": "F",
            "code": "F",
            "p1Uid": w["SF1"],
            "p2Uid": w["SF2"],
            "winnerUid": None,
            "createdAt": now,
        })
        batch.commit()
        return {"ok": True, "created": "F"}

    # Finish tournament if Final done
    if fs and all_done(fs):
        champ = fs[0]["winnerUid"]
        batch.set(t_ref, {"status": "done", "championUid": champ, "finishedAt": now}, merge=True)
        batch.commit()
        return {"ok": True, "done": True, "championUid": champ}

    return {"ok": True, "message": "Nothing to advance yet"}

@router.post("/matches/{match_id}/clear-winner")
async def clear_bracket_winner(match_id: str, admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    m_ref = t_ref.collection("matches").document(match_id)
    m_doc = m_ref.get()
    if not m_doc.exists:
        raise HTTPException(404, "Match not found")

    m = m_doc.to_dict() or {}
    if m.get("stage") != "bracket":
        raise HTTPException(400, "Not a bracket match")

    m_ref.set({
        "winnerUid": None,
        "updatedByEmail": admin.get("email"),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }, merge=True)

    return {"ok": True}

class SetScoreBody(BaseModel):
    score1: int
    score2: int

@router.post("/matches/{match_id}/set-score")
async def set_score(match_id: str, body: SetScoreBody, admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    m_ref = t_ref.collection("matches").document(match_id)
    m_doc = m_ref.get()
    if not m_doc.exists:
        raise HTTPException(404, "Match not found")

    m = m_doc.to_dict() or {}
    if m.get("stage") != "bracket":
        raise HTTPException(400, "Not a bracket match")

    best_of = int(m.get("bestOf", 3))
    needed = best_of // 2 + 1

    s1 = max(0, min(body.score1, needed))
    s2 = max(0, min(body.score2, needed))

    # Auto winner when someone reaches needed wins
    winner = None
    if s1 >= needed and s1 > s2:
        winner = m.get("p1Uid")
    elif s2 >= needed and s2 > s1:
        winner = m.get("p2Uid")

    m_ref.set({
        "score1": s1,
        "score2": s2,
        "winnerUid": winner,     # auto-set / auto-clear
        "updatedAt": _now(),
        "updatedByUid": admin["uid"],
        "updatedByEmail": admin.get("email"),
    }, merge=True)

    return {"ok": True, "score1": s1, "score2": s2, "winnerUid": winner}