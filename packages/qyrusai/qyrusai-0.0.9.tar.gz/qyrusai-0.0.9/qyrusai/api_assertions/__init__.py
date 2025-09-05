from typing import Optional
from .headers import AsyncHeaderAssertions, SyncHeaderAssertions
from .json_body import AsyncJSONBodyAssertions, SyncJSONBodyAssertions
from .json_path import AsyncJSONPathAssertions, SyncJSONPathAssertions
from .json_schema import AsyncJSONSchemaAssertions, SyncJSONSchemaAssertions
from .all_assertions import AsyncAllAssertions, SyncAllAssertions


class AsyncAssertions:

    def __init__(self, api_key: str, base_url: str,
                 gateway_token: str) -> None:
        self.headers = AsyncHeaderAssertions(api_key, base_url, gateway_token)
        self.jsonbody = AsyncJSONBodyAssertions(api_key, base_url,
                                                gateway_token)
        self.jsonpath = AsyncJSONPathAssertions(api_key, base_url,
                                                gateway_token)
        self.jsonschema = AsyncJSONSchemaAssertions(api_key, base_url,
                                                    gateway_token)
        self.all_assertions = AsyncAllAssertions(api_key, base_url,
                                                 gateway_token)


class SyncAssertions:

    def __init__(self, api_key: str, base_url: str,
                 gateway_token: str) -> None:
        self.headers = SyncHeaderAssertions(api_key, base_url, gateway_token)
        self.jsonbody = SyncJSONBodyAssertions(api_key, base_url,
                                               gateway_token)
        self.jsonpath = SyncJSONPathAssertions(api_key, base_url,
                                               gateway_token)
        self.jsonschema = SyncJSONSchemaAssertions(api_key, base_url,
                                                   gateway_token)
        self.all_assertions = SyncAllAssertions(api_key, base_url,
                                                gateway_token)
