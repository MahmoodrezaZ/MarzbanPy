from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccessToken:
    access_token: str
    token_type: str

    def __init__(self, *, access_token: str, token_type: str) -> None:
        self.access_token = access_token
        self.token_type = token_type


@dataclass
class Admin:
    username: str
    is_sudo: bool
    password: str

    def __init__(
        self, *, username: str, is_sudo: bool = True, password: str = None
    ) -> None:
        self.username = username
        self.is_sudo = is_sudo
        self.password = password


class Proxy:
    name: str
    id: str

    def __init__(self, *, name: str, id: str = None):
        self.name = name
        self.id = id


@dataclass
class Subscription:
    token: str
    url: str
    client_type: str

    def __init__(self, *, token: str, client_type: str = None):
        self.token = token
        self.url = f"/sub/{self.token}"
        self.client_type = client_type


class Status:
    ACTIVE = "active"
    DISABLED = "disabled"
    LIMITED = "limited"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"


class LimitStrategy:
    NO_RESET = "no_reset"
    DAY = "day"
    WEEK = "week"
    MONTH = "MONTH"
    YEAR = "year"


class ClientType:
    SINGBOX = "sing-box"
    CLASHMETA = "clash-meta"
    CLASH = "clash"
    OUTLINE = "outline"
    V2RAY = "v2ray"


@dataclass
class SubscriptionInfo:
    proxies: list[Proxy]
    expire: int | None
    data_limit: int
    data_limit_reset_strategy: int | str
    inbounds: list[str]
    note: str | None
    sub_updated_at: datetime | None
    sub_last_user_agent: str | None
    online_at: datetime | None
    on_hold_expire_duration: int | None
    on_hold_timeout: datetime | None
    username: str
    status: Status
    used_traffic: int
    lifetime_used_traffic: int
    created_at: datetime
    links: list[str]
    subscription_url: str
    excluded_inbounds: list[str]

    def __init__(
        self,
        *,
        proxies: list[Proxy],
        expire: int | None,
        data_limit: int,
        data_limit_reset_strategy: int | str,
        inbounds: list[str],
        note: str | None,
        sub_updated_at: datetime | None,
        sub_last_user_agent: str | None,
        online_at: datetime | None,
        on_hold_expire_duration: int | None,
        on_hold_timeout: datetime | None,
        username: str,
        status: Status,
        used_traffic: int,
        lifetime_used_traffic: int,
        created_at: datetime,
        links: list[str],
        subscription_url: str,
        excluded_inbounds: list[str],
    ):
        self.proxies = proxies
        self.expire = expire
        self.data_limit = data_limit
        self.data_limit_reset_strategy = data_limit_reset_strategy
        self.inbounds = inbounds
        self.note = note
        self.sub_updated_at = sub_updated_at
        self.sub_last_user_agent = sub_last_user_agent
        self.online_at = online_at
        self.on_hold_expire_duration = on_hold_expire_duration
        self.on_hold_timeout = on_hold_timeout
        self.username = username
        self.status = status
        self.used_traffic = used_traffic
        self.lifetime_used_traffic = lifetime_used_traffic
        self.created_at = created_at
        self.links = links
        self.subscription_url = subscription_url
        self.excluded_inbounds = excluded_inbounds


class SystemStats:
    version: str
    mem_total: int
    mem_used: int
    cpu_cores: int
    cpu_usage: int
    total_user: int
    users_active: int
    incoming_bandwidth: int
    outgoing_bandwidth: int
    incoming_bandwidth_speed: int
    outgoing_bandwidth_speed: int

    def __init__(
        self,
        *,
        version: str,
        mem_total: int,
        mem_used: int,
        cpu_cores: int,
        cpu_usage: int,
        total_user: int,
        users_active: int,
        incoming_bandwidth: int,
        outgoing_bandwidth: int,
        incoming_bandwidth_speed: int,
        outgoing_bandwidth_speed: int,
    ) -> None:
        self.version = version
        self.mem_total = mem_total
        self.mem_used = mem_used
        self.cpu_cores = cpu_cores
        self.cpu_usage = cpu_usage
        self.total_user = total_user
        self.users_active = users_active
        self.incoming_bandwidth = incoming_bandwidth
        self.outgoing_bandwidth = outgoing_bandwidth
        self.incoming_bandwidth_speed = incoming_bandwidth_speed
        self.outgoing_bandwidth_speed = outgoing_bandwidth_speed
