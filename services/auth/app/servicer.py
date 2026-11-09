import grpc
import jwt
from sqlalchemy import select

from auth_client import auth_pb2, auth_pb2_grpc
from app.blacklist import blacklist
from app.database import SessionLocal
from app.models import Role, User
from app.security import create_token, decode_token, hash_password, verify_password

ROLE_TO_PROTO = {
    Role.ADMINISTRATOR: auth_pb2.ADMINISTRATOR,
    Role.MAINTAINER: auth_pb2.MAINTAINER,
}
PROTO_TO_ROLE = {proto: role for role, proto in ROLE_TO_PROTO.items()}

MAX_PASSWORD_BYTES = 72


def to_proto_user(user: User) -> auth_pb2.User:
    return auth_pb2.User(
        uid=str(user.uid),
        username=user.username,
        role=ROLE_TO_PROTO[user.role],
        is_active=user.is_active,
    )


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    def _validate(self, token: str, context: grpc.ServicerContext, code: grpc.StatusCode) -> dict:
        if blacklist.contains(token):
            context.abort(code, "Token has been invalidated")
        try:
            return decode_token(token)
        except jwt.InvalidTokenError:
            blacklist.add(token)
            context.abort(code, "Token is invalid or expired")

    def _require_admin(self, token: str, context: grpc.ServicerContext) -> dict:
        claims = self._validate(token, context, grpc.StatusCode.PERMISSION_DENIED)
        if claims["role"] != Role.ADMINISTRATOR.value:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Administrator role required")
        return claims

    def Login(self, request, context):
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == request.username))

        if user is None:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid username or password")
        if not user.is_active:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Account is not active")
        if user.password is None or not verify_password(request.password, user.password):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid username or password")

        return auth_pb2.TokenResponse(token=create_token(user))

    def ListUsers(self, request, context):
        self._require_admin(request.token, context)

        with SessionLocal() as db:
            users = db.scalars(select(User).order_by(User.username)).all()

        return auth_pb2.UserList(users=[to_proto_user(user) for user in users])

    def CreateUser(self, request, context):
        self._require_admin(request.token, context)

        username = request.username.strip()
        if not username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Username is required")
        if request.role not in PROTO_TO_ROLE:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Role must be ADMINISTRATOR or MAINTAINER")

        with SessionLocal() as db:
            if db.scalar(select(User).where(User.username == username)) is not None:
                context.abort(grpc.StatusCode.ALREADY_EXISTS, "Username already exists")

            db.add(User(username=username, role=PROTO_TO_ROLE[request.role], password=None, is_active=False))
            db.commit()

        return auth_pb2.OperationResponse(success=True, message=f"User '{username}' created")

    def DeactivateUser(self, request, context):
        claims = self._require_admin(request.token, context)

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == request.username))
            if user is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
            if str(user.uid) == claims["sub"]:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "You cannot deactivate your own account")
            if not user.is_active:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Account is already inactive")

            user.is_active = False
            db.commit()

        return auth_pb2.OperationResponse(success=True, message=f"User '{request.username}' deactivated")

    def ActivateUser(self, request, context):
        if not request.password:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Password is required")
        if len(request.password.encode()) > MAX_PASSWORD_BYTES:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Password is too long")

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.username == request.username))
            if user is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
            if user.is_active:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Account is already active")
            if user.password is not None:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Account already has a password")

            user.password = hash_password(request.password)
            user.is_active = True
            db.commit()

        return auth_pb2.OperationResponse(success=True, message=f"User '{request.username}' activated")

    def ValidateToken(self, request, context):
        claims = self._validate(request.token, context, grpc.StatusCode.UNAUTHENTICATED)
        return auth_pb2.TokenClaims(sub=claims["sub"], role=ROLE_TO_PROTO[Role(claims["role"])])

    def DestroyToken(self, request, context):
        self._validate(request.token, context, grpc.StatusCode.UNAUTHENTICATED)
        blacklist.add(request.token)
        return auth_pb2.OperationResponse(success=True, message="Token destroyed")
