from dataclasses import dataclass


@dataclass
class AccessToken:
    access_token: str
    token_type: str

    def __init__(
        self,
        access_token: str,
        token_type: str
    ) -> None:
        self.access_token = access_token
        self.token_type = token_type
