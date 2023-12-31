from contextlib import AbstractContextManager
from httpx import Client, URL
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from exceptions import (
    BearerRequired,
    ResponseException
)
from models import AccessToken


class MarzbanState(Enum):
    UNOPENED = auto()
    OPENED = auto()
    CLOSED = auto()

# TODO: Create method for all Admin operations
# TODO: Create object for the requests and responses
# TODO: Study more about decoraters and fix them

@dataclass
class Marzban(AbstractContextManager):
    def __init__(self, base_url: URL | str) -> None:
        if isinstance(base_url, str):
            base_url = URL(base_url)

        self.base_url = base_url

        self._state = MarzbanState.UNOPENED
        
        self.__bearer = None

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
    def __flush_state(force_bearer: bool=False):
        def decorator(func: callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                args = list(args)
                self = args[0]
                args = tuple(args)
                if force_bearer:
                    if self.__bearer is None:
                        raise BearerRequired("Bearer Token should be created before using methods")

                if self._state == MarzbanState.UNOPENED:
                    self.__client = Client()
                    self._state = MarzbanState.OPENED
                    return func(*args, **kwargs)
                
                elif self._state == MarzbanState.OPENED:
                    return func(*args, **kwargs)

                raise RuntimeError("Can't do any action while connection is closed")
            
            return wrapper
        return decorator

    @__flush_state()
    def get_admin_token(self, username: str, password: str):
        request = self.__client.post(
            self.base_url.join("/api/admin/token"),
            data={"username": username, "password": password},
        )

        if request.status_code == 200:
            response = request.json()
            result = AccessToken(
                response.get("access_token"), 
                response.get("token_type")
            )
            self.__bearer = result.access_token
            return result
        
        elif request.status_code == 401:
            raise ResponseException("Invalid Login Credential")
        
    
    @__flush_state(force_bearer=True)
    def get_current_admin(self):
        request = self.__client.get(
            self.base_url.join("/api/admin"),
            headers={'Authorization': f'Bearer {self.__bearer}'}
        )
        
        print(request.json())
