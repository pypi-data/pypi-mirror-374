from typing import Optional
from .vision_nova import Async_VisionNova_create, Async_VisionNova_verify, Sync_VisionNova_create, Sync_VisionNova_verify

class Async_Vision_Nova:
    def __init__(self, api_key: str, base_url: str, gateway_token: str) -> None:
        self.generate_test = Async_VisionNova_create(api_key, base_url, gateway_token)
        self.verify_accessibility = Async_VisionNova_verify(api_key, base_url, gateway_token)
        
class Sync_Vision_Nova:
    def __init__(self, api_key: str, base_url: str, gateway_token: str) -> None:
        self.generate_test = Sync_VisionNova_create(api_key, base_url, gateway_token)
        self.verify_accessibility = Sync_VisionNova_verify(api_key, base_url, gateway_token)
        