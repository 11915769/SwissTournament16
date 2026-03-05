import os
from datetime import datetime, timezone
from google.cloud import firestore

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GCLOUD_PROJECT"] = "kniffelswiss16"

db = firestore.Client()
print("Using project:", db.project)

TOURNAMENT_ID = "main"
t_ref = db.collection("tournaments").document(TOURNAMENT_ID)

# DO NOT overwrite tournament fields; just ensure doc exists
t_ref.set({"exists": True}, merge=True)

now = datetime.now(timezone.utc).isoformat()
players_ref = t_ref.collection("players")

for i in range(16):
    uid = f"test_player_{i+1}"
    players_ref.document(uid).set({
        "uid": uid,
        "name": f"Test Player {i+1}",
        "email": f"player{i+1}@test.com",
        "joinedAt": now,
        "wins": 0,
        "losses": 0,
        "eliminated": False,
    }, merge=True)

print("Added 16 players to emulator")