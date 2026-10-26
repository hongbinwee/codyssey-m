import json
from functools import lru_cache
from app.core.config import get_settings


@lru_cache
def get_firestore_client():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as exc:
        raise RuntimeError("firebase-admin 패키지가 설치되어 있지 않습니다.") from exc

    settings = get_settings()

    if not firebase_admin._apps:
        if settings.firebase_service_account_json:
            try:
                service_account = json.loads(settings.firebase_service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON이 올바른 JSON이 아닙니다.") from exc
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred)
        elif settings.firebase_service_account_path:
            cred = credentials.Certificate(settings.firebase_service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # GOOGLE_APPLICATION_CREDENTIALS 등 Application Default Credentials 사용 가능
            firebase_admin.initialize_app()

    return firestore.client()
