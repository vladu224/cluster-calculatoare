import enum
from dataclasses import dataclass

import grpc

from auth_client import auth_pb2, auth_pb2_grpc


class Role(str, enum.Enum):
    ADMINISTRATOR = "administrator"
    MAINTAINER = "maintainer"


ROLE_TO_PROTO = {
    Role.ADMINISTRATOR: auth_pb2.ADMINISTRATOR,
    Role.MAINTAINER: auth_pb2.MAINTAINER,
}
PROTO_TO_ROLE = {proto: role for role, proto in ROLE_TO_PROTO.items()}


@dataclass(frozen=True)
class UserInfo:
    uid: str
    username: str
    role: Role
    is_active: bool


@dataclass(frozen=True)
class TokenClaims:
    sub: str
    username: str
    role: Role


class AuthError(Exception):
    def __init__(self, code: grpc.StatusCode, message: str):
        super().__init__(f"{code.name}: {message}")
        self.code = code
        self.message = message


class AuthClient:
    def __init__(self, target: str = "localhost:50051", timeout: float = 5.0):
        self._channel = grpc.insecure_channel(target)
        self._stub = auth_pb2_grpc.AuthServiceStub(self._channel)
        self._timeout = timeout

    def _call(self, method, request):
        try:
            return method(request, timeout=self._timeout)
        except grpc.RpcError as error:
            raise AuthError(error.code(), error.details()) from error

    def login(self, username: str, password: str) -> str:
        response = self._call(self._stub.Login, auth_pb2.LoginRequest(username=username, password=password))
        return response.token

    def list_users(self, token: str) -> list[UserInfo]:
        response = self._call(self._stub.ListUsers, auth_pb2.TokenRequest(token=token))
        return [
            UserInfo(uid=user.uid, username=user.username, role=PROTO_TO_ROLE[user.role], is_active=user.is_active)
            for user in response.users
        ]

    def create_user(self, token: str, username: str, role: Role) -> str:
        request = auth_pb2.CreateUserRequest(token=token, username=username, role=ROLE_TO_PROTO[role])
        return self._call(self._stub.CreateUser, request).message

    def deactivate_user(self, token: str, username: str) -> str:
        request = auth_pb2.DeactivateUserRequest(token=token, username=username)
        return self._call(self._stub.DeactivateUser, request).message

    def activate_user(self, username: str, password: str) -> str:
        request = auth_pb2.ActivateUserRequest(username=username, password=password)
        return self._call(self._stub.ActivateUser, request).message

    def validate_token(self, token: str) -> TokenClaims:
        response = self._call(self._stub.ValidateToken, auth_pb2.TokenRequest(token=token))
        return TokenClaims(sub=response.sub, username=response.username, role=PROTO_TO_ROLE[response.role])

    def destroy_token(self, token: str) -> str:
        return self._call(self._stub.DestroyToken, auth_pb2.TokenRequest(token=token))

    def close(self) -> None:
        self._channel.close()

    def __enter__(self) -> "AuthClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()