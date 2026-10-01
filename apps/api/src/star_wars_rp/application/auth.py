from datetime import datetime, timedelta, timezone
import uuid

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.config import get_settings
from star_wars_rp.errors import Conflict, Unauthorized
from star_wars_rp.modules.auth.models import Principal


_password_hash = PasswordHash.recommended()


def normalize_username(username: str) -> str:
    return username.strip().lower()


def register_principal(db: Session, username: str, password: str) -> Principal:
    username = normalize_username(username)
    if db.scalar(select(Principal).where(Principal.username == username)):
        raise Conflict("Username already exists")

    principal = Principal(username=username, password_hash=_password_hash.hash(password))
    db.add(principal)
    db.commit()
    db.refresh(principal)
    return principal


def authenticate_principal(db: Session, username: str, password: str) -> Principal:
    principal = db.scalar(select(Principal).where(Principal.username == normalize_username(username)))
    if principal is None or not _password_hash.verify(password, principal.password_hash):
        raise Unauthorized("Invalid username or password")
    return principal


def create_login_token(principal_id: uuid.UUID) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_token_minutes)
    return jwt.encode(
        {"sub": str(principal_id), "exp": expires},
        settings.auth_secret,
        algorithm="HS256",
    )


def decode_login_token(token: str) -> uuid.UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
        subject = payload.get("sub")
        if not subject:
            raise Unauthorized("Invalid authentication token")
        return uuid.UUID(subject)
    except (InvalidTokenError, ValueError, TypeError) as exc:
        raise Unauthorized("Invalid or expired authentication token") from exc
