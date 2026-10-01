from dataclasses import dataclass
from functools import lru_cache
import os


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    auth_secret: str
    auth_cookie_name: str
    auth_cookie_secure: bool
    auth_token_minutes: int


@lru_cache
def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    auth_secret = os.getenv("AUTH_SECRET")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")
    if not auth_secret or len(auth_secret) < 32:
        raise RuntimeError("AUTH_SECRET must be at least 32 characters")

    return Settings(
        database_url=database_url,
        auth_secret=auth_secret,
        auth_cookie_name=os.getenv("AUTH_COOKIE_NAME", "sw_rp_session"),
        auth_cookie_secure=_bool_env("AUTH_COOKIE_SECURE", False),
        auth_token_minutes=int(os.getenv("AUTH_TOKEN_MINUTES", "480")),
    )
