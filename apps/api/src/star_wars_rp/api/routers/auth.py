from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import AuthRequest, PrincipalOut
from star_wars_rp.application.auth import authenticate_principal, create_login_token, register_principal
from star_wars_rp.config import get_settings
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=PrincipalOut, status_code=201)
def register(body: AuthRequest, db: Session = Depends(get_db)):
    principal = register_principal(db, body.username, body.password)
    return PrincipalOut(id=principal.id, username=principal.username)


@router.post("/login", response_model=PrincipalOut)
def login(body: AuthRequest, response: Response, db: Session = Depends(get_db)):
    principal = authenticate_principal(db, body.username, body.password)
    settings = get_settings()
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=create_login_token(principal.id),
        max_age=settings.auth_token_minutes * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )
    return PrincipalOut(id=principal.id, username=principal.username)


@router.post("/logout", status_code=204)
def logout(response: Response):
    settings = get_settings()
    response.delete_cookie(settings.auth_cookie_name, path="/")
    return Response(status_code=204)


@router.get("/me", response_model=PrincipalOut)
def me(principal: Principal = Depends(current_principal)):
    return PrincipalOut(id=principal.id, username=principal.username)
