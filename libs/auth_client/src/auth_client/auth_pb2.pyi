from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ADMINISTRATOR: _ClassVar[Role]
    MAINTAINER: _ClassVar[Role]
ROLE_UNSPECIFIED: Role
ADMINISTRATOR: Role
MAINTAINER: Role

class LoginRequest(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class TokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class TokenResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("uid", "username", "role", "is_active")
    UID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    uid: str
    username: str
    role: Role
    is_active: bool
    def __init__(self, uid: _Optional[str] = ..., username: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ..., is_active: _Optional[bool] = ...) -> None: ...

class UserList(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, users: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("token", "username", "role")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    token: str
    username: str
    role: Role
    def __init__(self, token: _Optional[str] = ..., username: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ...) -> None: ...

class DeactivateUserRequest(_message.Message):
    __slots__ = ("token", "username")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    token: str
    username: str
    def __init__(self, token: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class ActivateUserRequest(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class TokenClaims(_message.Message):
    __slots__ = ("sub", "role")
    SUB_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    sub: str
    role: Role
    def __init__(self, sub: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ...) -> None: ...

class OperationResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...
