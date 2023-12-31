from contextlib import AbstractContextManager
from httpx import Client, URL
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps


class MarzbanState(Enum):
    UNOPENED = auto()
    OPENED = auto()
    CLOSED = auto()

# TODO: creating request & response objects

@dataclass
class Marzban(AbstractContextManager):
    def __init__(self, base_url: URL | str) -> None:
        if isinstance(base_url, str):
            base_url = URL(base_url)

        self.base_url = base_url

        self._state = MarzbanState.UNOPENED

    def close(self):
        if self._state != MarzbanState.CLOSED:
            self._state = MarzbanState.CLOSED
            self.__client.close()

    def __enter__(self):
        if self._state != MarzbanState.UNOPENED:
            raise RuntimeError(
                {
                    MarzbanState.CLOSED: "Can't reopen the connection when it is closed",
                    MarzbanState.OPENED: "Can't reopen the connection while it is open",
                }[self._state]
            )

        self.__client = Client()
        self._state = MarzbanState.OPENED

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._state != MarzbanState.OPENED:
            raise RuntimeError(
                {
                    MarzbanState.CLOSED: "Can't close the connection when it is already closed",
                    MarzbanState.UNOPENED: "Can't close the connection while it is still unopened",
                }[self._state]
            )
        
        self.__client.close()
        self._state = MarzbanState.CLOSED
            
        

    @staticmethod
    def __flush_state(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            self = args[0]
            args = tuple(args)
            if self._state == MarzbanState.UNOPENED:
                self.__client = Client()
                self._state = MarzbanState.OPENED
                return func(*args, **kwargs)
            
            elif self._state == MarzbanState.OPENED:
                return func(*args, **kwargs)

            raise RuntimeError("Can't do any action while connection is closed")
        
        return wrapper

    @__flush_state
    def get_admin_token(self, username: str, password: str):
        request = self.__client.post(
            self.base_url.join("/api/admin/token"),
            data={"username": username, "password": password},
        )

        return request.json()
