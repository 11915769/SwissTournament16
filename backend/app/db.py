import os
from google.cloud import firestore
from app.auth import init_firebase  # adjust import if needed

_db = None

def get_db():
    global _db
    if _db:
        return _db

    # Emulator
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        print("Using Firestore Emulator")
        _db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "kniffelswiss16"))
        return _db

    # Production
    init_firebase()

    project = (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("FIREBASE_PROJECT_ID")
    )
    if not project:
        raise RuntimeError("Set GOOGLE_CLOUD_PROJECT (your GCP/Firebase project id)")

    _db = firestore.Client(project=project)
    return _db