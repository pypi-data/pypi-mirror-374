from typing import Optional
# from qyrusai.data_amplifier.data_amplifier import AsyncDataAmplifier
from .data_amplifier import AsyncDataAmplifier, SyncDataAmplifier

class AsyncAmplifier:
    def __init__(self, api_key: str) -> None:
        self.data_amplifier = AsyncDataAmplifier(api_key)
        
class SyncAmplifier:
    def __init__(self, api_key: str) -> None:
        self.data_amplifier = SyncDataAmplifier(api_key)