# from urllib.parse import urljoin
# import pytest
# from unittest.mock import MagicMock, patch
# from unittest.mock import AsyncMock
# from qyrusai.configs import Configurations
# from qyrusai.data_amplifier.data_amplifier import AsyncDataAmplifier, AsyncHTTPClient, DataAmplifierResponse, SyncDataAmplifier
# from unittest.mock import patch
# import asyncio
# from qyrusai._exceptions import AuthorizationException, RequestException, EntityException, ErrorException


# @pytest.fixture
# def async_data_amplifier():
#     return AsyncDataAmplifier(api_key="1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d")


# @pytest.fixture
# def sync_data_amplifier():
#     return SyncDataAmplifier(api_key="1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d")


# @pytest.fixture
# def expected_data():
#     return {
#         "data": {
#             "name": ["Aisha Khan", "Rajesh Mehta", "Priya Sharma"]
#         },
#         "status": True,
#         "message": ""
#     }


# """Mock HTTP responses to imitate Data Amplifier"""


# @pytest.mark.asyncio
# async def test_async_api_aseertion_create_method(async_data_amplifier,
#                                                  expected_data):
#     with patch.object(AsyncHTTPClient, 'post',
#                       return_value=expected_data) as mock_post:
#         data_count = 0
#         data = [{
#             "column_name": "name",
#             "column_description": "name",
#             "column_restriction": "no restrictions",
#             "column_values": ["Sameer Seikh", "Sunil Dutt"]
#         }]
#         result = await async_data_amplifier.amplify(data, data_count)
#         print(result)
#         assert isinstance(result, DataAmplifierResponse)
#         assert result.status == True
#         assert 'name' in result.data
#         assert isinstance(result.data, dict)
#         assert isinstance(result.data['name'], list)


# @pytest.mark.asyncio
# async def test_create_with_invalid_api_key():
#     invalid_api_key = " "
#     client = AsyncDataAmplifier(api_key=invalid_api_key)

#     with patch('qyrusai._rest.AsyncHTTPClient.post',
#                new_callable=AsyncMock) as mock_post:
#         # Setup the mock object to raise AuthorizationException when the mock is called
#         mock_post.return_value.status_code = 401
#         mock_post.side_effect = AuthorizationException(
#             "Unauthorized: Access is denied due to invalid credentials.")
#         data_count = 3
#         data = [{
#             "column_name": "name",
#             "column_description": "name",
#             "column_restriction": "no restrictions",
#             "column_values": ["Sameer Seikh", "Sunil Dutt"]
#         }]
#         with pytest.raises(AuthorizationException) as exc_info:
#             await client.amplify(data, data_count)

#         print(f"For api key: {invalid_api_key} results in {exc_info.value}")
#         assert isinstance(exc_info.value, AuthorizationException)
#         assert exc_info.value.message in str(exc_info.value)


# # @pytest.mark.parametrize("data, exception, message", [
# #     (" 0.789", EntityException,
# #      "The server could not understand the request due to invalid syntax or incorrect input data."
# #      ),
# # ])
# # def test_create_with_various_inputs(sync_data_amplifier, data, exception,
# #                                     message):
# #     with patch('qyrusai._rest.SyncHTTPClient.post') as mocked_post:
# #         data_count = 1
# #         if exception == EntityException:
# #             mocked_post.side_effect = exception(message)

# #         with pytest.raises(exception) as exc_info:
# #             sync_data_amplifier.amplify(data, data_count)
# #         print(f"For user description : {data} results in {exc_info.value}")
# #         assert isinstance(exc_info.value, exception)
# #         assert message in str(exc_info.value)
