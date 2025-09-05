
from typing import Optional
from .api_builder import AsyncApiBuilder,SyncApiBuilder

class AsyncBuilder:
    def __init__(self, api_key: str) -> None:
        self.api_builder = AsyncApiBuilder(api_key)
        
class SyncBuilder:
    def __init__(self,api_key: str) -> None:
        self.api_builder = SyncApiBuilder(api_key)