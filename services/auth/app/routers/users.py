import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RefreshToken, Role, User, UserStatus
from app.schemas import UserCreate, UserOut, UserStatusUpdate
from app.security import hash_password, require_admin


router = APIRouter(prefix="/users", tags=["users"])


def get_user_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_managed_user(db: Session, user_id: uuid.UUID, admin: User) -> User:
    """Fetch a user that the admin is allowed to change or delete: never an Admin account."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot modify your own account")

    user = get_user_or_404(db, user_id)
    if user.role == Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin accounts cannot be modified")
    return user


@router.get("", response_model=list[UserOut])
def list_users(
    role: Role | None = None,
    status: UserStatus | None = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = select(User).order_by(User.created_at)
    if role is not None:
        query = query.where(User.role == role)
    if status is not None:
        query = query.where(User.status == status)

    return db.scalars(query).all()


@router.post("", response_model=UserOut, status_code=201)
def create_maintainer(
    body: UserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    conflict = HTTPException(status_code=409, detail="Username or email already in use")

    existing = db.scalar(select(User).where(or_(User.username == body.username, User.email == body.email)))
    if existing is not None:
        raise conflict

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role=Role.MAINTAINER,
        created_by=admin.id,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request took the same username or email between the check and the insert
        db.rollback()
        raise conflict
    db.refresh(user)

    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_user_or_404(db, user_id)


@router.patch("/{user_id}/status", response_model=UserOut)
def update_status(
    user_id: uuid.UUID,
    body: UserStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_managed_user(db, user_id, admin)
    user.status = body.status

    if body.status == UserStatus.DISABLED:
        db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True))

    db.commit()
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_managed_user(db, user_id, admin)
    db.delete(user)
    db.commit()

    return Response(status_code=204)
