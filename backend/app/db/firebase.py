"""Firebase Admin SDK initialisation (singleton)."""

import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
_db = None


def init_firebase():
    """Initialize Firebase app once."""
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL,
        })
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialised for project: %s", settings.FIREBASE_PROJECT_ID)


def get_db() -> firestore.Client:
    """Return Firestore client (initialise if needed)."""
    global _db
    if _db is None:
        init_firebase()
        _db = firestore.client()
    return _db
