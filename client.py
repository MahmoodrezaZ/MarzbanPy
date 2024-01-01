from contextlib import AbstractContextManager
from httpx import Client, URL
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from exceptions import (
    BearerRequired,
    BadResponse,
    ExistanceError,
    PermissionDenied,
    ValidationError,
    NotExistsError,
)
from models import AccessToken, Admin


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
    def __flush_state(force_bearer: bool = True):
        def decorator(func: callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                args = list(args)
                self = args[0]
                args = tuple(args)

                if force_bearer:
                    if self.__bearer is None:
                        raise BearerRequired("Bearer Token should be created")

                if self._state == MarzbanState.UNOPENED:
                    self.__client = Client()
                    self._state = MarzbanState.OPENED

                    return func(*args, **kwargs)

                elif self._state == MarzbanState.OPENED:
                    return func(*args, **kwargs)

                raise RuntimeError("Can't do any action while connection is closed")

            return wrapper

        return decorator

    @__flush_state(force_bearer=False)
    def get_admin_token(self, admin: Admin):
        request = self.__client.post(
            self.base_url.join("/api/admin/token"),
            data={"username": admin.username, "password": admin.password},
        )

        if request.status_code == 200:
            response = request.json()
            result = AccessToken(
                access_token=response.get("access_token"),
                token_type=response.get("token_type"),
            )
            self.__bearer = result.access_token
            self.__client.headers.update({"Authorization": f"Bearer {self.__bearer}"})
            return result

        elif request.status_code == 401:
            raise ValidationError("Invalid Login Credential")

    @__flush_state()
    def get_current_admin(self):
        request = self.__client.get(self.base_url.join("/api/admin"))

        if request.status_code != 200:
            raise RuntimeError("Internal exception")

        response = request.json()

        match response.get("detail"):
            case "Not authenticated":
                raise BearerRequired("Bearer Token should be created")

        return Admin(username=response.get("username"), is_sudo=response.get("is_sudo"))

    @__flush_state()
    def create_admin(self, admin: Admin) -> Admin:
        request = self.__client.post(
            self.base_url.join("/api/admin"),
            json={
                "username": admin.username,
                "is_sudo": admin.is_sudo,
                "password": admin.password,
            },
        )

        response = request.json()

        match response.get("detail"):
            case "Admin already exists":
                raise ExistanceError("Admin already exists")
            case "You're not allowed":
                raise PermissionDenied(
                    "Permission denied for this bearer token and admin user"
                )
            case "Validation Error":
                raise ValidationError("Request Validation Error")
            case "Not authenticated":
                raise BearerRequired("Bearer Token should be created")
            case _:
                if response.get("username") != admin.username:
                    raise BadResponse("I/O Conflict")

        return admin

    @__flush_state()
    def set_admin(self, admin: Admin) -> Admin:
        request = self.__client.put(
            self.base_url.join(f"/api/admin/{admin.username}"),
            json={"password": admin.password, "is_sudo": admin.is_sudo},
        )

        response = request.json()

        match response.get("detail"):
            case "Admin already exists":
                raise NotExistsError("Admin not found")
            case "You're not allowed":
                raise PermissionDenied(
                    "Permission denied for this bearer token and admin user"
                )
            case "Validation Error":
                raise ValidationError("Request Validation Error")
            case "Not authenticated":
                raise BearerRequired("Bearer Token should be created")
            case _:
                if response.get("username") != admin.username:
                    raise BadResponse("I/O Conflict")

        return admin

    @__flush_state()
    def delete_admin(self, admin: Admin):
        request = self.__client.delete(
            self.base_url.join(f"/api/admin/{admin.username}")
        )

        response = request.json()

        match response.get("detail"):
            case "Admin already exists":
                raise NotExistsError("Admin not found")
            case "You're not allowed":
                raise PermissionDenied(
                    "Permission denied for this bearer token and admin user"
                )
            case "Validation Error":
                raise ValidationError("Request Validation Error")
            case "Not authenticated":
                raise BearerRequired("Bearer Token should be created")
            case _:
                if response.get("username") != admin.username:
                    raise BadResponse("I/O Conflict")

        return admin
    
    @__flush_state()
    def get_admins(self):
        request = self.__client.get(self.base_url.join("/api/admins"))

        response = request.json()
        users = []
        for user in response:
            users.append(
                Admin(username=user.get("username"), is_sudo=user.get("is_sudo"))
            )

        return users

    @__flush_state()
    def get_admins_generator(self):
        request = self.__client.get(self.base_url.join("/api/admins"))

        response = request.json()

        for user in response:
            yield Admin(username=user.get("username"), is_sudo=user.get("is_sudo"))
    
    @__flush_state()
    def get_admin(self, admin: Admin):
        request = self.__client.get(self.base_url.join(f"/api/admins?username={admin.username}"))
        
        response = request.json()

        for user in response:
            return Admin(username=user.get("username"), is_sudo=user.get("is_sudo"))
