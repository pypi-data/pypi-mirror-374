from qyrusai.configs import Configurations
from typing import Optional
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient


class AsyncApiBuilder:

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

    async def build(self, email: str, user_description: str):
        """Give user description to build APIs.

        Args:
            email (str): User mail.
            user_description (str): User description.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getApiBuilderContextPath("build"))

        data = {"email": email, "user_description": user_description}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)

        # print(f"response_data [ASYNC] (api build) : {response_data}")
        # print(
        #     f"response_data [ASYNC] (api build) TYPE == >> : {type(response_data)}"
        # )

        return response_data


class SyncApiBuilder:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # token_valid = Configurations.verifyToken(
        #     self.api_key
        # )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # if not token_valid:
        #     raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    def build(self, email: str, user_description: str):
        """Give user description to build APIs.

        Args:
            email (str): User mail.
            user_description (str): User description.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getApiBuilderContextPath("build"))

        data = {"email": email, "user_description": user_description}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)

        # print(f"response_data [SYNC] (api build) : {response_data}")
        # print(
        #     f"response_data [SYNC] (api build) TYPE == >> : {type(response_data)}"
        # )

        return response_data
