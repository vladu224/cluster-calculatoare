from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Role, User
from app.security import hash_password

def seed_admin(db: Session) -> None:
    """
    Seed the database with an admin user if it doesn't exist.
    """
    existing = db.scalar(select(User).where(User.role == Role.ADMIN).limit(1))
    if existing is not None:
        return  # Admin user already exists

    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        role=Role.ADMIN,
    )
    db.add(admin)
    db.commit()