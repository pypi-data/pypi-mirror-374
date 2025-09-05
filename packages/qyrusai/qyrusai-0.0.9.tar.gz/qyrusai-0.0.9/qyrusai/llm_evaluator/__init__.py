from typing import Optional
from .evaluator import AsyncLLMEvaluator, SyncLLMEvaluator


class AsyncEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.evaluator = AsyncLLMEvaluator(api_key, base_url, gateway_token)


class SyncEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.evaluator = SyncLLMEvaluator(api_key, base_url, gateway_token)
