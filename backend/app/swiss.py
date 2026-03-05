from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set
import random

@dataclass(frozen=True)
class PlayerRec:
    uid: str
    wins: int
    losses: int
    buchholz: int

def compute_standings(players: List[str], matches: List[dict]) -> List[PlayerRec]:
    wins: Dict[str, int] = {uid: 0 for uid in players}
    losses: Dict[str, int] = {uid: 0 for uid in players}
    opponents: Dict[str, List[str]] = {uid: [] for uid in players}

    for m in matches:
        p1 = m["p1Uid"]
        p2 = m.get("p2Uid")  # may be None for bye
        is_bye = bool(m.get("bye"))

        if p2:
            opponents[p1].append(p2)
            opponents[p2].append(p1)

        w = m.get("winnerUid")
        if not w:
            continue

        # bye counts as win for p1
        if is_bye and w == p1:
            wins[p1] += 1
            continue

        if not p2:
            continue

        if w == p1:
            wins[p1] += 1
            losses[p2] += 1
        elif w == p2:
            wins[p2] += 1
            losses[p1] += 1

    buchholz: Dict[str, int] = {uid: 0 for uid in players}
    for uid in players:
        buchholz[uid] = sum(wins.get(opp, 0) for opp in opponents[uid])

    recs = [PlayerRec(uid=uid, wins=wins[uid], losses=losses[uid], buchholz=buchholz[uid]) for uid in players]
    recs.sort(key=lambda r: (-r.wins, -r.buchholz, r.uid))
    return recs

def round1_pairings(player_uids: List[str], seed: int | None = None) -> List[Tuple[str, str]]:
    uids = list(player_uids)
    rnd = random.Random(seed)
    rnd.shuffle(uids)
    if len(uids) % 2 != 0:
        raise ValueError("Swiss pairing expects even number of players (got odd).")
    return [(uids[i], uids[i+1]) for i in range(0, len(uids), 2)]

def avoid_rematch_pairings(standings: List[PlayerRec], played_pairs: Set[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Simple Swiss pairing for rounds 2+: pair by standings order, avoid rematches by local swapping.
    Good enough for 16 players; we can improve later if needed.
    """
    uids = [r.uid for r in standings]
    pairs: List[Tuple[str, str]] = []
    i = 0
    while i < len(uids):
        a = uids[i]
        # try find b not rematched
        j = i + 1
        while j < len(uids):
            b = uids[j]
            key = (a, b) if a < b else (b, a)
            if key not in played_pairs:
                # pair a with b
                pairs.append((a, b))
                # remove b from list by swapping into i+1 and continue
                uids.pop(j)
                uids.pop(i)
                # restart from same i (since we removed current)
                i = 0
                break
            j += 1
        else:
            # couldn't avoid rematch; pair with next
            b = uids[i+1]
            pairs.append((a, b))
            uids.pop(i+1)
            uids.pop(i)
            i = 0

    return pairs

def swiss_active_players(
    standings: List[PlayerRec],
    win_target: int = 3,
    loss_target: int = 3,
) -> List[PlayerRec]:
    # only players who are not yet "done" in swiss
    return [r for r in standings if r.wins < win_target and r.losses < loss_target]