# from configs import Configurations
from qyrusai.configs import Configurations
from qyrusai._types import DataAmplifierResponse
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient


class AsyncDataAmplifier:

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

    async def amplify(self, data, data_count):
        """To amplify your tabular data.

        Args:
            data (list): Data to be amplified.
            data_count (str): Give a slider value.
        
        Returns:
            DataAmplifierResponse: List of dictionaries representing the created/amplified data.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getDataAmplifierContextPath())

        body = {
            "data": data,
            "data_count": data_count,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()

        response_data = await async_client.post(url, body, headers)

        # print(f"response_data (ASYNC-DA) : {response_data}")
        # print(
        #     f"response_data (ASYNC-DA) TYPE == >> : {type(response_data)}"
        # )

        return DataAmplifierResponse(**response_data)


class SyncDataAmplifier:

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

    def amplify(self, data, data_count):
        """To amplify your tabular data.

        Args:
            data (list): Data to be amplified.
            data_count (str): Give a slider value.
        
        Returns:
            DataAmplifierResponse: List of dictionaries representing the created/amplified data.
        """
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url,
                      Configurations.getDataAmplifierContextPath())

        body = {
            "data": data,
            "data_count": data_count,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()

        response_data = sync_client.post(url, body, headers)

        # print(f"response_data (SYNC-DA) : {response_data}")
        # print(
        #     f"response_data (SYNC-DA) TYPE == >> : {type(response_data)}"
        # )

        return DataAmplifierResponse(**response_data)
