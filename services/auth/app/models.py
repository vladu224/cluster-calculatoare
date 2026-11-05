import enum
import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.database import Base


class Role(str, enum.Enum):
    ADMINISTRATOR = "administrator"
    MAINTAINER = "maintainer"


class User(Base):
    __tablename__ = "users"

    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role", create_type=False, values_callable=lambda roles: [r.value for r in roles])
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)