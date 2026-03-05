import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

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

    # Production Firebase
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if not service_account:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_PATH is not set")

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)

    _db = firestore.Client()
    return _db