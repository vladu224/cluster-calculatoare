from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import RefreshToken, User, UserStatus
from app.schemas import AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.security import (
    create_access_token,
    generate_refresh_token,
    get_current_user,
    hash_token,
    verify_password,
)

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=403, detail="Account is disabled")

    now = datetime.now(timezone.utc)
    refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_days),
        )
    )
    user.last_login_at = now
    db.commit()

    return TokenResponse(access_token=create_access_token(user), refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(body.refresh_token)))

    if stored is None or stored.revoked or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    if stored.user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return AccessTokenResponse(access_token=create_access_token(stored.user))


@router.post("/logout", status_code=204)
def logout(
    body: RefreshRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stored = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_token(body.refresh_token),
            RefreshToken.user_id == user.id,
        )
    )

    if stored is not None:
        stored.revoked = True
        db.commit()

    return Response(status_code=204)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user