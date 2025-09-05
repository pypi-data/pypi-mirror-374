# from nova.nova import AsyncNovaJira, AsyncNovaUserDescription
# from nova.nova import AsyncNovaJira, AsyncNovaUserDescription
from typing import Optional
from .nova import AsyncNovaJira, AsyncNovaUserDescription, SyncNovaJira, SyncNovaUserDescription, AsyncNovaRally, SyncNovaRally


class AsyncNova:
    # def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
    def __init__(self, api_key: str, base_url: str,
                 gateway_token: str) -> None:
        self.from_jira = AsyncNovaJira(api_key, base_url, gateway_token)
        self.from_description = AsyncNovaUserDescription(
            api_key, base_url, gateway_token)
        self.from_rally = AsyncNovaRally(api_key, base_url, gateway_token)


class SyncNova:
    # def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
    def __init__(self, api_key: str, base_url: str,
                 gateway_token: str) -> None:
        self.from_jira = SyncNovaJira(api_key, base_url, gateway_token)
        self.from_description = SyncNovaUserDescription(
            api_key, base_url, gateway_token)
        self.from_rally = SyncNovaRally(api_key, base_url, gateway_token)
