# from _rest import AsyncHTTPClient, SyncHTTPClient
import asyncio
import os
from typing import Optional
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient
from qyrusai.configs import Configurations
from qyrusai._types import CreateScenariosResponse, JiraDetails
from urllib.parse import urljoin
import json


class AsyncNovaJira:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # token_valid = Configurations.verifyToken(api_key) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        # if not token_valid:
        #     raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    async def create(self, jira_endpoint: str, jira_api_token: str,
                     jira_username: str,
                     jira_id: str) -> CreateScenariosResponse:
        """Creates Test Scenarios using a JIRA ID
        Connects to a JIRA instance using provided credentials and domain URL, then generates test scenarios based on the specified JIRA Ticket ID.

        Args:
            jira_details (JiraDetails): A model containing the parameters
                required for connecting to JIRA.

        Returns:
            CreateScenariosResponse: A model representing the response of the operation with
                the success status, message, and a list of scenarios if successful.
        """
        # print(jira_api_token, jira_endpoint, jira_id, jira_username)

        # Join the base URL and the context path
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url, Configurations.getNovaContextPath("jira"))

        data = {
            "jira_endpoint": jira_endpoint,
            "jira_api_token": jira_api_token,
            "jira_username": jira_username,
            "jira_id": jira_id
        }

        # JiraDetails.validate(data)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)
        # print(f"response_data (createScenariosFromJira) : {response_data}")
        # print(
        #     f"response_data (createScenariosFromJira) TYPE == >> : {type(response_data)}"
        # )

        return CreateScenariosResponse(**response_data)


class SyncNovaJira:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(
            api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    def create(self, jira_endpoint: str, jira_api_token: str,
               jira_username: str, jira_id: str) -> CreateScenariosResponse:
        """Creates Test Scenarios using a JIRA ID
        Connects to a JIRA instance using provided credentials and domain URL, then generates test scenarios based on the specified JIRA Ticket ID.

        Args:
            jira_details (JiraDetails): A model containing the parameters
                required for connecting to JIRA.

        Returns:
            CreateScenariosResponse: A model representing the response of the operation with
                the success status, message, and a list of scenarios if successful.
        """
        # print(jira_api_token, jira_endpoint, jira_id, jira_username)

        # Join the base URL and the context path
        token_valid = Configurations.verifyToken(
            self.api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        url = urljoin(self.base_url, Configurations.getNovaContextPath("jira"))

        data = {
            "jira_endpoint": jira_endpoint,
            "jira_api_token": jira_api_token,
            "jira_username": jira_username,
            "jira_id": jira_id
        }

        # JiraDetails.validate(data)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }  # Headers if required

        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)
        # print(f"response_data (createScenariosFromJira) : {response_data}")
        # print(
        #     f"response_data (createScenariosFromJira) TYPE == >> : {type(response_data)}"
        # )

        return CreateScenariosResponse(**response_data)


class AsyncNovaUserDescription:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(
            api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    async def create(self, user_description: str) -> CreateScenariosResponse:
        """Creates Test Scenarios using a User Description.
        
        Args:
            user_description (str): A description by user to create test scenarios.

        Returns:
             CreateScenariosResponse: A model representing the response of the operation with
                the success status, message, and a list of scenarios if successful.
        """

        url = urljoin(self.base_url, Configurations.getNovaContextPath("user"))

        data = {
            "user_description": user_description,
        }

        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.gateway_token,
            "Custom": self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)
        # print("📁.....", response_data)
        return CreateScenariosResponse(**response_data)


class SyncNovaUserDescription:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(
            api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    def create(self, user_description: str) -> CreateScenariosResponse:
        """Creates Test Scenarios using a User Description.
        
        Args:
            user_description (str): A description by user to create test scenarios.

        Returns:
            CreateScenariosResponse: A model representing the response of the operation with
                the success status, message, and a list of scenarios if successful.
        """

        url = urljoin(self.base_url, Configurations.getNovaContextPath("user"))

        data = {
            "user_description": user_description,
        }

        headers = {
            'Content-Type': 'application/json',
            "Custom": self.api_key,
            "Authorization": "Bearer " + self.gateway_token
        }  # Headers if required
        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)
        # print("📁.....", response_data)
        return CreateScenariosResponse(**response_data)


class AsyncNovaRally:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(
            api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    async def create(self, TICKET_ID, WORKSPACE_NAME, RALLY_URL,
                     RALLY_API_KEY):

        url = urljoin(
            self.base_url,
            Configurations.getNovaContextPath("get_rally_workspaces"))
        # print(f"URL IN NOVA WORKSAPCE : {url}")

        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.gateway_token,
            "Custom": self.api_key
        }

        params = {"RALLY_URL": RALLY_URL, "RALLY_API_KEY": RALLY_API_KEY}

        async_client = AsyncHTTPClient()
        response = await async_client.get(url=url,
                                          params=params,
                                          headers=headers)
        if response:
            workspaces = response.get("workspaces", [])
            for workspace in workspaces:
                if workspace.get("_refObjectName") == WORKSPACE_NAME:
                    WORKSPACE_REF = workspace.get("_ref")
                    # print(f"WORKSPACE_REF for '{WORKSPACE_NAME}': {WORKSPACE_REF}")
                    ticket_details_url = urljoin(
                        self.base_url,
                        Configurations.getNovaContextPath(
                            "get_rally_ticket_details"))
                    ticket_params = {
                        "TICKET_ID": TICKET_ID,
                        "WORKSPACE_REF": WORKSPACE_REF,
                        "RALLY_API_KEY": RALLY_API_KEY,
                        "RALLY_URL": RALLY_URL
                    }

                    ticket_response = await async_client.get(
                        url=ticket_details_url,
                        params=ticket_params,
                        headers=headers)

                    # if ticket_response:
                    ticket_title = ticket_response.get("ticket_title", "")
                    description = ticket_response.get("description", "")

                    if ticket_title or description:
                        user_description = json.dumps({
                            "ticket_title":
                            ticket_title,
                            "description":
                            description
                        })
                        # if description:
                        async_description_instance = AsyncNovaUserDescription(
                            api_key=self.api_key)
                        async_description_response = await async_description_instance.create(
                            user_description)
                        # print(f"AsyncDescription Response: {async_description_response}")
                        return async_description_response

                    return CreateScenariosResponse(
                        ok=False,
                        message=
                        f"Description not found for for Workspace: {WORKSPACE_NAME} "
                    )

            return CreateScenariosResponse(
                ok=False,
                message=
                f"WORKSPACE_NAME : '{WORKSPACE_NAME}' not found in workspaces."
            )


class SyncNovaRally:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(
            api_key
        )  # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        # gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = base_url
        self.gateway_token = gateway_token

    def create(self, TICKET_ID, WORKSPACE_NAME, RALLY_URL, RALLY_API_KEY):

        url = urljoin(
            self.base_url,
            Configurations.getNovaContextPath("get_rally_workspaces"))

        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.gateway_token,
            "Custom": self.api_key
        }

        params = {"RALLY_URL": RALLY_URL, "RALLY_API_KEY": RALLY_API_KEY}

        sync_client = SyncHTTPClient()
        response = sync_client.get(url=url, params=params, headers=headers)
        if response:
            workspaces = response.get("workspaces", [])
            for workspace in workspaces:
                if workspace.get("_refObjectName") == WORKSPACE_NAME:
                    WORKSPACE_REF = workspace.get("_ref")
                    # print(f"WORKSPACE_REF for '{WORKSPACE_NAME}': {WORKSPACE_REF}")

                    ticket_details_url = urljoin(
                        self.base_url,
                        Configurations.getNovaContextPath(
                            "get_rally_ticket_details"))

                    ticket_params = {
                        "TICKET_ID": TICKET_ID,
                        "WORKSPACE_REF": WORKSPACE_REF,
                        "RALLY_API_KEY": RALLY_API_KEY,
                        "RALLY_URL": RALLY_URL
                    }

                    ticket_response = sync_client.get(url=ticket_details_url,
                                                      params=ticket_params,
                                                      headers=headers)

                    ticket_title = ticket_response.get("ticket_title", "")
                    description = ticket_response.get("description", "")

                    if ticket_title or description:
                        user_description = json.dumps({
                            "ticket_title":
                            ticket_title,
                            "description":
                            description
                        })
                        # if description:
                        sync_description_instance = SyncNovaUserDescription(
                            api_key=self.api_key)
                        sync_description_response = sync_description_instance.create(
                            user_description)
                        # print(f"SyncDescription Response: {sync_description_response}")
                        return sync_description_response

                    return CreateScenariosResponse(
                        ok=False,
                        message=
                        f"Ticket: '{TICKET_ID}' not found in {WORKSPACE_NAME} "
                    )

            return CreateScenariosResponse(
                ok=False,
                message=
                f"WORKSPACE_NAME : '{WORKSPACE_NAME}' not found in workspaces."
            )
