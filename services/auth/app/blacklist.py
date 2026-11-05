import threading
from datetime import datetime, timezone


class TokenBlacklist:
    def __init__(self) -> None:
        self._tokens: dict[str, datetime] = {}
        self._lock = threading.Lock()

    def add(self, token: str) -> None:
        with self._lock:
            self._tokens[token] = datetime.now(timezone.utc)

    def contains(self, token: str) -> bool:
        with self._lock:
            return token in self._tokens


blacklist = TokenBlacklist()
