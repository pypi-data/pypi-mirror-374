from qyrusai.configs import Configurations
from typing import Optional
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient
from qyrusai._types import AssertionResponseRequest


class AsyncJSONSchemaAssertions:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # token_valid = Configurations.verifyToken(
        #     api_key
        # )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # if not token_valid:
        #     raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    async def create(self, response: AssertionResponseRequest):
        """Generate JSONSchema Assertions.

        Args:
            response (AssertionResponseRequest): response

        Returns:
            _type_: Returns the list of JSON key ,value and desriptions.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getAPIAssertions("jsonschema"))

        data = {"response": response}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)

        # print(f"response_data [ASYNC] (JSON Schema Assertions) : {response_data}")
        # print(
        #     f"response_data [ASYNC] (JSON Schema Assertions) TYPE == >> : {type(response_data)}"
        # )

        return response_data


class SyncJSONSchemaAssertions:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # token_valid = Configurations.verifyToken(
        #     api_key
        # )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # if not token_valid:
        #     raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    def create(self, response: AssertionResponseRequest):
        """Generate JSONSchema Assertions.

        Args:
            response (AssertionResponseRequest): response

        Returns:
            _type_: Returns the list of JSON key ,value and desriptions.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getAPIAssertions("jsonschema"))

        data = {"response": response}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)

        # print(f"response_data [SYNC] (JSON Schema Assertions) : {response_data}")
        # print(
        #     f"response_data [SYNC] (JSON Schema Assertions) TYPE == >> : {type(response_data)}"
        # )

        return response_data
