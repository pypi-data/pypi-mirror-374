import httpx
import asyncio
from ._exceptions import AuthorizationException, RequestException, ErrorException, EntityException
from fastapi.responses import JSONResponse


class AsyncHTTPClient:

    async def post(self, url, data, headers=None):
        # print("\nURL (ASYNC) : ", url)
        # print("\nDATA for Service Call (ASYNC) : ", data)
        async with httpx.AsyncClient(timeout=600) as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                # print(f"Response status code: {response.status_code}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthorizationException(
                        "Unauthorized: Access is denied due to invalid credentials. Please provide valid authentication details to access this resource."
                    )
                elif response.status_code == 500:
                    raise RequestException(
                        "Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request."
                    )
                elif response.status_code in [422, 400]:
                    raise EntityException(
                        "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."
                    )
                else:
                    raise ErrorException("An unexpected error occurred")
            # except httpx.HTTPStatusError as e:
            #     # print(f"HTTPStatusError: {e}")
            except httpx.RequestError as e:
                print(f"RequestError: {e}")
                raise
            except asyncio.TimeoutError:
                print("Request timed out")
                raise
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise
    
    async def get(self, url, params=None, headers=None):
            async with httpx.AsyncClient(timeout=600) as client:
                try:
                    response = await client.get(url, params=params, headers=headers)
                    # print(f"URL:{url}, PARAMS:{params}, headers:{headers}")
                    # print(f"Response status code: {response.status_code}")
                    if response.status_code // 100 == 2:
                        # print(f"Raw response content: {response.text}")
                        return response.json()
                    elif response.status_code == 401:
                        raise AuthorizationException(
                            "Unauthorized: Access is denied due to invalid credentials. Please provide valid authentication details to access this resource."
                        )
                    elif response.status_code == 500:
                        raise RequestException(
                            "Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request."
                        )
                    elif response.status_code in [422, 400]:
                        raise EntityException(
                            "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."
                        )
                    else:
                        raise ErrorException("An unexpected error occurred")
                except httpx.RequestError as e:
                    print(f"RequestError: {e}")
                    raise
                except asyncio.TimeoutError:
                    print("Request timed out")
                    raise
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    raise            



class SyncHTTPClient:

    def post(self, url, data, headers=None):
        # print("\nURL (SYNC) : ", url)
        # print("\nDATA for Service Call (SYNC) : ", data)
        with httpx.Client(timeout=600) as client:
            try:
                response = client.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthorizationException(
                        "Unauthorized: Access is denied due to invalid credentials. Please provide valid authentication details to access this resource."
                    )
                elif response.status_code == 500:
                    raise RequestException(
                        "Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request."
                    )
                elif response.status_code in [422, 400]:
                    raise EntityException(
                        "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."
                    )
                else:
                    raise ErrorException("An unexpected error occurred")
            except httpx.RequestError as e:
                print(f"RequestError: {e}")
                raise
            except asyncio.TimeoutError:
                print("Request timed out")
                raise
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise

    def get(self, url, params=None, headers=None):
            with httpx.Client(timeout=600) as client:
                try:
                    response = client.get(url, params=params, headers=headers)
                    # print(f"URL:{url}, PARAMS:{params}, headers:{headers}")
                    # print(f"Response status code: {response.status_code}")
                    if response.status_code // 100 == 2:
                        # print(f"Raw response content: {response.text}")
                        return response.json()
                    elif response.status_code == 401:
                        raise AuthorizationException(
                            "Unauthorized: Access is denied due to invalid credentials. Please provide valid authentication details to access this resource."
                        )
                    elif response.status_code == 500:
                        raise RequestException(
                            "Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request."
                        )
                    elif response.status_code in [422, 400]:
                        raise EntityException(
                            "Bad Request: The server could not understand the request due to invalid syntax or incorrect input data."
                        )
                    else:
                        raise ErrorException("An unexpected error occurred")
                except httpx.RequestError as e:
                    print(f"RequestError: {e}")
                    raise
                except asyncio.TimeoutError:
                    print("Request timed out")
                    raise
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    raise            

