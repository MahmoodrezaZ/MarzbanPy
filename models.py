from dataclasses import dataclass


@dataclass
class AccessToken:
    access_token: str
    token_type: str

    def __init__(
        self,
        *,
        access_token: str,
        token_type: str
    ) -> None:
        self.access_token = access_token
        self.token_type = token_type


@dataclass
class Admin:
    username: str
    is_sudo: bool
    password: str
    
    def __init__(
        self,
        *,
        username: str,
        is_sudo: bool = True,
        password: str = None
    ) -> None:
        self.username = username
        self.is_sudo = is_sudo
        self.password = password
