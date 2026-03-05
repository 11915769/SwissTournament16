from __future__ import annotations
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.constants import TOURNAMENT_ID
from app.db import get_db
from app.deps import require_admin
from app.swiss import round1_pairings, compute_standings, avoid_rematch_pairings, swiss_active_players

router = APIRouter(prefix="/admin/swiss", tags=["admin-swiss"])

def _now():
    return datetime.now(timezone.utc).isoformat()

class SetWinnerBody(BaseModel):
    winnerUid: str

@router.post("/start")
async def start_swiss(admin=Depends(require_admin)):
    """
    - requires tournament exists
    - requires status == registration
    - requires 2..16 players, even count
    - sets status=swiss, currentRound=1
    - creates round 1 matches (random)
    """
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    if t.get("status") != "registration":
        raise HTTPException(400, f"Cannot start swiss from status={t.get('status')}")

    players = [p.to_dict() for p in t_ref.collection("players").stream()]
    player_uids = [p["uid"] for p in players if p.get("uid")]

    if len(player_uids) < 2:
        raise HTTPException(400, "Not enough players")
    if len(player_uids) % 2 != 0:
        raise HTTPException(400, "Player count must be even for Swiss pairing")

    pairings = round1_pairings(player_uids)

    now = datetime.now(timezone.utc).isoformat()

    batch = db.batch()

    # update tournament
    batch.set(t_ref, {
        "status": "swiss",
        "currentRound": 1,
        "startedAt": now,
        "startedByUid": admin["uid"],
        "startedByEmail": admin.get("email"),
    }, merge=True)

    # create matches
    matches_ref = t_ref.collection("matches")
    for (p1, p2) in pairings:
        match_id = uuid.uuid4().hex
        doc_ref = matches_ref.document(match_id)
        batch.set(doc_ref, {
            "id": match_id,
            "stage": "swiss",
            "round": 1,
            "p1Uid": p1,
            "p2Uid": p2,
            "winnerUid": None,
            "createdAt": now,
        })

    batch.commit()
    return {"ok": True, "round": 1, "matchCount": len(pairings)}

@router.post("/next-round")
async def next_round(admin=Depends(require_admin)):
    """
    - requires status == swiss
    - requires currentRound < swissRounds
    - requires all matches in currentRound finished
    - computes standings and generates next round pairings avoiding rematches
    """
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    t_doc = t_ref.get()
    if not t_doc.exists:
        raise HTTPException(400, "Tournament not created yet")
    t = t_doc.to_dict() or {}

    if t.get("status") != "swiss":
        raise HTTPException(400, f"Cannot generate next round from status={t.get('status')}")

    swiss_rounds = int(t.get("swissRounds", 5))
    current_round = int(t.get("currentRound", 0))
    if current_round <= 0:
        raise HTTPException(400, "Swiss not started")
    if current_round >= swiss_rounds:
        raise HTTPException(400, "Swiss rounds already complete")

    # load players
    players_docs = [p.to_dict() for p in t_ref.collection("players").stream()]
    active_players = [p for p in players_docs if not p.get("eliminated")]
    active_uids = [p["uid"] for p in active_players if p.get("uid")]

    # load all swiss matches so far
    matches = [m.to_dict() for m in t_ref.collection("matches").where("stage", "==", "swiss").stream()]
    # ensure all matches in current round are finished
    cur_round_matches = [m for m in matches if int(m.get("round", 0)) == current_round]
    if not cur_round_matches:
        raise HTTPException(400, "No matches found for current round")
    if any(not m.get("winnerUid") for m in cur_round_matches):
        raise HTTPException(400, "Not all matches in current round are finished")

    standings_all = compute_standings([p["uid"] for p in players_docs if p.get("uid")], matches)

    standings_active = [r for r in standings_all if r.uid in active_uids and r.losses < 3]
    pairing_uids = [r.uid for r in standings_active]

    # build set of played pairs (skip byes)
    played_pairs = set()
    for m in matches:
        a = m.get("p1Uid")
        b = m.get("p2Uid")
        if not a or not b:
            continue
        played_pairs.add((a, b) if a < b else (b, a))

    next_round_num = current_round + 1

    # who is still active in swiss (not 3W / not 3L)
    active_recs = swiss_active_players(standings_active, win_target=3, loss_target=3)

    # choose bye if needed (should rarely happen, but safe)
    bye_uid = None
    if len(active_recs) % 2 == 1:
        # choose lowest-ranked active player for bye
        bye_uid = active_recs[-1].uid
        active_recs = [r for r in active_recs if r.uid != bye_uid]

    # now pairings is guaranteed even-length
    pairings = avoid_rematch_pairings(active_recs, played_pairs)

    now = datetime.now(timezone.utc).isoformat()
    batch = db.batch()

    batch.set(t_ref, {"currentRound": next_round_num}, merge=True)

    matches_ref = t_ref.collection("matches")

    # ✅ create BYE exactly once
    if bye_uid:
        match_id = uuid.uuid4().hex
        batch.set(matches_ref.document(match_id), {
            "id": match_id,
            "stage": "swiss",
            "round": next_round_num,
            "p1Uid": bye_uid,
            "p2Uid": None,
            "bye": True,
            "winnerUid": bye_uid,  # auto win
            "createdAt": now,
        })

    # ✅ create normal matches
    for (p1, p2) in pairings:
        match_id = uuid.uuid4().hex
        batch.set(matches_ref.document(match_id), {
            "id": match_id,
            "stage": "swiss",
            "round": next_round_num,
            "p1Uid": p1,
            "p2Uid": p2,
            "winnerUid": None,
            "createdAt": now,
        })

    batch.commit()
    return {"ok": True, "round": next_round_num, "matchCount": len(pairings) + (1 if bye_uid else 0)}

@router.post("/matches/{match_id}/set-winner")
async def set_winner(match_id: str, body: SetWinnerBody, admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    m_ref = t_ref.collection("matches").document(match_id)
    m_doc = m_ref.get()
    if not m_doc.exists:
        raise HTTPException(404, "Match not found")

    m = m_doc.to_dict() or {}
    winner = body.winnerUid

    p1 = m.get("p1Uid")
    p2 = m.get("p2Uid")
    if winner not in (p1, p2):
        raise HTTPException(400, "winnerUid must be one of the two players")

    # write winner
    m_ref.set({
        "winnerUid": winner,
        "updatedAt": _now(),
        "updatedByUid": admin["uid"],
        "updatedByEmail": admin.get("email"),
    }, merge=True)

    # compute loser and eliminate if 3 losses
    loser = p2 if winner == p1 else p1
    if loser:
        # recompute losses from all swiss matches (including this one)
        matches = [x.to_dict() for x in t_ref.collection("matches").where("stage", "==", "swiss").stream()]
        standings = compute_standings(
            players=[p.to_dict()["uid"] for p in t_ref.collection("players").stream()],
            matches=matches
        )
        losses_by_uid = {r.uid: r.losses for r in standings}
        if losses_by_uid.get(loser, 0) >= 3:
            t_ref.collection("players").document(loser).set({
                "eliminated": True,
                "eliminatedAt": _now(),
                "eliminatedReason": "3_losses",
            }, merge=True)

    return {"ok": True}

@router.post("/matches/{match_id}/clear-winner")
async def clear_winner(match_id: str, admin=Depends(require_admin)):
    db = get_db()
    t_ref = db.collection("tournaments").document(TOURNAMENT_ID)
    m_ref = t_ref.collection("matches").document(match_id)
    m_doc = m_ref.get()
    if not m_doc.exists:
        raise HTTPException(404, "Match not found")

    m_ref.set({
        "winnerUid": None,
        "updatedByEmail": admin.get("email"),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }, merge=True)

    return {"ok": True}