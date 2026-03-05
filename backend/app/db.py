import os
from google.cloud import firestore

from .auth import init_firebase  # add this import

_db = None

def get_db():
    global _db
    if _db:
        return _db

    # If emulator is running
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        print("Using Firestore Emulator")
        _db = firestore.Client(project="kniffelswiss16")
        return _db

    # Production Firebase: init app (supports JSON or PATH via auth.py)
    init_firebase()

    _db = firestore.Client()
    return _db