import os, json
import firebase_admin
from firebase_admin import credentials

_initialized = False

def init_firebase():
    global _initialized
    if _initialized or firebase_admin._apps:
        _initialized = True
        return

    sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        cred = credentials.Certificate(json.loads(sa_json))
        firebase_admin.initialize_app(cred)
        _initialized = True
        return

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if not path:
        raise RuntimeError("Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH")
    firebase_admin.initialize_app(credentials.Certificate(path))
    _initialized = True