import os
from dataclasses import dataclass
from getpass import getpass

from auth_client import AuthClient, AuthError, Role


@dataclass
class ConsoleState:
    token: str | None = None


ROLE_CHOICES = [Role.ADMINISTRATOR, Role.MAINTAINER]


def require_token(state: ConsoleState) -> str | None:
    if state.token is None:
        print("Please login first.")
    return state.token

def login(client: AuthClient, state: ConsoleState) -> None:
    username = input("Username: ").strip()
    password = getpass("Password: ")
    state.token = client.login(username, password)
    print(f"Logged in. Token: {state.token}")

def activate_account(client: AuthClient, state: ConsoleState) -> None:
    username = input("Username: ").strip()
    password = getpass("New password: ")
    print(client.activate_user(username, password))

def list_users(client: AuthClient, state: ConsoleState) -> None:
    token = require_token(state)
    if token is None:
        return

    users = client.list_users(token)
    print(f"\n{'UID':<38} {'USERNAME':<20} {'ROLE':<15} ACTIVE")
    for user in users:
        print(f"{user.uid:<38} {user.username:<20} {user.role.value:<15} {user.is_active}")

def create_user(client: AuthClient, state: ConsoleState) -> None:
    token = require_token(state)
    if token is None:
        return

    username = input("Username: ").strip()
    for index, role in enumerate(ROLE_CHOICES, start=1):
        print(f" {index}. {role.value}")
    choice = input("Role: ").strip()

    if not choice.isdigit() or not 1 <= int(choice) <= len(ROLE_CHOICES):
        print("Invalid role.")
        return

    print(client.create_user(token, username, ROLE_CHOICES[int(choice) - 1]))

def deactivate_user(client: AuthClient, state: ConsoleState) -> None:
    token = require_token(state)
    if token is None:
        return

    username = input("Username to deactivate: ").strip()
    print(client.deactivate_user(token, username))

def validate_token(client: AuthClient, state: ConsoleState) -> None:
    token = input("Token (Enter = current token): ").strip() or state.token
    if token is None:
        print("No token given and you are not logged in.")
        return

    claims = client.validate_token(token)
    print(f"Token is valid. sub={claims.sub} role={claims.role.value}")

def logout(client: AuthClient, state: ConsoleState) -> None:
    token = require_token(state)
    if token is None:
        return

    print(client.destroy_token(token))
    state.token = None


MENU = [
    ("Login", login),
    ("Activate account", activate_account),
    ("List users", list_users),
    ("Create user", create_user),
    ("Deactivate user", deactivate_user),
    ("Validate token", validate_token),
    ("Logout (destroy token)", logout),
]


def main() -> None:
    target = os.getenv("AUTH_TARGET", "localhost:50051")
    state = ConsoleState()

    with AuthClient(target) as client:
        while True:
            print("\n=== Auth Console ===")
            for index, (label, _) in enumerate(MENU, start=1):
                print(f"{index}. {label}")
            print("0. Exit")

            choice = input("> ").strip()
            if choice == "0":
                break
            if not choice.isdigit() or not 1 <= int(choice) <= len(MENU):
                print("Invalid option.")
                continue

            _, action = MENU[int(choice) - 1]
            try:
                action(client, state)
            except AuthError as error:
                print(f"Error [{error.code.name}]: {error.message}")


if __name__ == "__main__":
    main()