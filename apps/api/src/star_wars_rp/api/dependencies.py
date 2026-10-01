from fastapi import Depends, Request
from sqlalchemy.orm import Session

from star_wars_rp.application.auth import decode_login_token
from star_wars_rp.config import get_settings
from star_wars_rp.db import get_db
from star_wars_rp.errors import Unauthorized
from star_wars_rp.modules.auth.models import Principal


def current_principal(
    request: Request,
    db: Session = Depends(get_db),
) -> Principal:
    settings = get_settings()
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        raise Unauthorized("Authentication required")
    principal_id = decode_login_token(token)
    principal = db.get(Principal, principal_id)
    if principal is None:
        raise Unauthorized("Authentication principal no longer exists")
    return principal
