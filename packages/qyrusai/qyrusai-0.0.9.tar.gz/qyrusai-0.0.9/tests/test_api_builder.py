# from urllib.parse import urljoin
# import pytest
# from unittest.mock import MagicMock, patch
# from unittest.mock import AsyncMock
# from qyrusai.configs import Configurations
# from qyrusai.api_builder.api_builder import AsyncApiBuilder, AsyncHTTPClient,SyncHTTPClient,SyncApiBuilder
# from unittest.mock import patch
# import asyncio
# from qyrusai._exceptions import AuthorizationException, RequestException, EntityException, ErrorException


# @pytest.fixture
# def async_api_builder():
#     return AsyncApiBuilder(api_key="test_api_key")

# @pytest.fixture
# def sync_api_builder():
#     return SyncApiBuilder(api_key="test_api_key")


# @pytest.fixture
# def response_data():
#     return {
#         "openapi": "3.0.0",
#         "info": {
#             "title": "Home Loan Microservice",
#             "version": "1.0.0"
#         },
#         "paths": {
#             "/loans": {
#                 "post": {
#                     "summary": "Apply for Loan",
#                     "description": "Allow users to apply for a loan.",
#                     "requestBody": {
#                         "required": True,
#                         "content": {
#                             "application/json": {
#                                 "schema": {
#                                     "type": "object",
#                                     "properties": {
#                                         "userId": {
#                                             "type": "integer"
#                                         },
#                                         "loanAmount": {
#                                             "type": "number"
#                                         }
#                                     },
#                                     "example": {
#                                         "userId": 1,
#                                         "loanAmount": 200000,
#                                     }
#                                 }
#                             }
#                         }
#                     },
#                     "responses": {
#                         "200": {
#                             "description":
#                             "Loan application created successfully.",
#                             "content": {
#                                 "application/json": {
#                                     "schema": {
#                                         "type": "object",
#                                         "properties": {
#                                             "loanId": {
#                                                 "type": "integer"
#                                             },
#                                             "status": {
#                                                 "type": "string"
#                                             }
#                                         },
#                                         "example": {
#                                             "loanId": 101,
#                                             "status": "pending"
#                                         }
#                                     }
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }


# """Mock HTTP responses to imitate API Bilder"""


# @pytest.mark.asyncio
# async def test_async_api_aseertion_create_method(async_api_builder,
#                                                  response_data):
#     with patch.object(AsyncHTTPClient, 'post',
#                       return_value=response_data) as mock_post:
#         api_design_description = "Create a Home Loan application microservice with APIs to apply for loan"
#         result = await async_api_builder.build(
#             email="", user_description=api_design_description)
#         assert isinstance(result, dict)


# def response_for_invalid_input(url, data, headers):
#     invalid_values = ["67.09", "None"]
#     # Here we're assuming the actual key you're checking against is 'json_schema'
#     if str(data.get("description")) in invalid_values:
#         return {
#             'message':
#             "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."
#         }


# """Test the create function with invalid inputs:"""


# @pytest.mark.parametrize("description", ["67.09", "None"])
# @pytest.mark.asyncio
# async def test_create_with_invalid_input(async_api_builder, description):
#     with patch.object(AsyncHTTPClient,
#                       'post',
#                       side_effect=response_for_invalid_input) as mock_post:
#         # Prepare the data structure as it's expected by the .post method
#         data = {'description': description}
#         result = await async_api_builder.build(email="", user_description=data)
#         print(f"For description : {data} results in {result['message']}")
#         assert result[
#             'message'] == "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."


# @pytest.mark.parametrize("data, exception, message", [
#     (" 0.789", EntityException,
#      "The server could not understand the request due to invalid syntax or incorrect input data."
#      ),
# ])
# def test_create_with_various_inputs(sync_api_builder, data, exception,
#                                           message):
#     with patch('qyrusai._rest.SyncHTTPClient.post') as mocked_post:
#         # Set the expected side effect or return value based on the input
#         if exception == EntityException:
#             mocked_post.side_effect = exception(message)

#         with pytest.raises(exception) as exc_info:
#             sync_api_builder.build(email="", user_description=data)
#         print(f"For user description : {data} results in {exc_info.value}")
#         assert isinstance(exc_info.value, exception)
#         assert message in str(exc_info.value)


# @pytest.mark.asyncio
# async def test_create_with_invalid_api_key():
#     invalid_api_key = " "
#     client = AsyncApiBuilder(api_key=invalid_api_key)

#     with patch('qyrusai._rest.AsyncHTTPClient.post',
#                new_callable=AsyncMock) as mock_post:
#         # Setup the mock object to raise AuthorizationException when the mock is called
#         mock_post.return_value.status_code = 401
#         mock_post.side_effect = AuthorizationException(
#             "Unauthorized: Access is denied due to invalid credentials.")

#         with pytest.raises(AuthorizationException) as exc_info:
#             await client.build(email="", user_description="create apis")

#         print(f"For api key: {invalid_api_key} results in {exc_info.value}")
#         assert isinstance(exc_info.value, AuthorizationException)
#         assert exc_info.value.message in str(exc_info.value)
