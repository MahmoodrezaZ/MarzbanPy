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
from models import (
    AccessToken,
    Admin,
    Subscription,
    SubscriptionInfo,
    Proxy,
    LimitStrategy,
    Status,
    ClientType,
    SystemStats,
    Inbound
)
from datetime import datetime

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
    def iget_admins(self):
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

    @__flush_state()
    def subscription(self, subscription: Subscription):
        request = self.__client.get( 
            self.base_url.join(f"/sub/{subscription.token}/{subscription.client_type}")
        )
        
        return request.text
    
    def subscription_url_generator(self, subscription: Subscription) -> str:
        return str(self.base_url.join(subscription.url))
    
    @__flush_state()
    def subscription_info(self, subscription: Subscription) -> SubscriptionInfo:
        request = self.__client.get(
            self.base_url.join(f"/sub/{subscription.token}/info")
        )
        
        response = request.json()
        
        return SubscriptionInfo(
            proxies=[Proxy(name=proxy.get("name"), id=proxy.get("id")) for proxy in response.get("proxies")],
            expire=response.get("expire"),
            data_limit=response.get("data_limit"),
            data_limit_reset_strategy=response.get("data_limit_reset_strategy"),
            inbounds=[
                Inbound(
                    tag=inbound.get("tag"),
                    protocol=inbound.get("protocol"),
                    network=inbound.get("network"),
                    tls=inbound.get("tls"),
                    port=inbound.get("port")
                )
                for inbound in response.get('inbounds')
            ],
            note=response.get("note"),
            sub_updated_at=datetime.strftime(response.get("sub_updated_at")),
            sub_last_user_agent=response.get("sub_last_user_agent"),
            online_at=datetime.strftime(response.get("online_at")),
            on_hold_expire_duration=response.get("on_hold_expire_duration"),
            on_hold_timeout=datetime.strftime(response.get("on_hold_timeout")),
            username=response.get("username"),
            status=response.get("status"),
            used_traffic=response.get("used_traffic"),
            lifetime_used_traffic=response.get("lifetime_used_traffic"),
            created_at=datetime.strftime(response.get("created_at")),
            links=response.get("links"),
            subscription_url=response.get("subscription_url"),
            excluded_inbounds=response.get("excluded_inbounds")
        )
        
    @__flush_state()
    def get_system_stats(self):
        request = self.__client.get(
            "/api/system"
        )
        
        response = request.json()
        
        return SystemStats(
            version=response.get("version"),
            mem_total=response.get("mem_total"),
            mem_used=response.get("mem_used"),
            cpu_cores=response.get("cpu_cores"),
            cpu_usage=response.get("cpu_usage"),
            total_user=response.get("total_user"),
            users_active=response.get("users_active"),
            incoming_bandwidth=response.get("incoming_bandwidth"),
            outgoing_bandwidth=response.get("outgoing_bandwidth"),
            incoming_bandwidth_speed=response.get("incoming_bandwidth_speed"),
            outgoing_bandwidth_speed=response.get("outgoing_bandwidth_speed")
        )
        
    @__flush_state()
    def get_inbounds(self):
        request = self.__client.get(
            self.base_url.join("/api/inbounds")
        )
        
        response = request.json()
        result = {}
        
        for key in response.keys():
            result[key] = [
                Inbound(
                    tag=inbound.get("tag"),
                    protocol=inbound.get("protocol"),
                    network=inbound.get("network"),
                    tls=inbound.get("tls"),
                    port=inbound.get("port")
                )
                for inbound in response.get(key)
            ]
        
        return result
    
    @__flush_state()
    def iget_inbounds(self):
        request = self.__client.get(
            self.base_url.join("/api/inbounds")
        )
        
        response = request.json()
        
        for key in response.keys():
            result = {
                key: [
                    Inbound(
                        tag=inbound.get("tag"),
                        protocol=inbound.get("protocol"),
                        network=inbound.get("network"),
                        tls=inbound.get("tls"),
                        port=inbound.get("port")
                    )
                    for inbound in response.get(key)
                ]
            }

            yield result
    
    #TODO
    @__flush_state()
    def get_hosts(self):
        request = self.__client.get(
            self.base_url.join("/api/hosts")
        )
    
    @__flush_state
    def modify_hosts(self):
        pass