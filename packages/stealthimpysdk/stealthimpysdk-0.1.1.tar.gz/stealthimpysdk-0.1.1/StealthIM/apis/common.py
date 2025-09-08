import dataclasses
from typing import Any

import aiohttp

from StealthIM import logger


@dataclasses.dataclass
class Result:
    code: int
    msg: str


@dataclasses.dataclass
class NoValResult:
    result: Result


async def request(
        url: str,
        method: str,
        data: dict = None,
        body: dict = None,
        headers: dict = None,
        retry: int = 3
) -> dict[str, Any]:
    """
    Make a request to the server.

    Args:
        url (str): The URL of the server.
        method (str): The HTTP method to use (default is "GET").
        data (dict): The data to send in the request (default is None).
        body (dict): The body of the request (default is None).
        headers (dict): The headers to include in the request (default is None).
        retry (int): The number of times to retry the request in case of failure (default is 3).

    Returns:
        dict[str, Any]: The response data from the server.
    Raises:
        RuntimeError: If the server returns an internal error too many times.
    """
    logger.debug(f"Request url: {url}")
    logger.debug(f"Method: {method}, Data: {data}, Body: {body}, Header: {headers}")
    current_retry = 0
    while current_retry < retry:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, data=data, headers=headers, json=body) as response:
                if response.status != 200:
                    raise RuntimeError(f"Request failed with status: {response.status}")
                response_data = await response.json()

                if 900 <= response_data["result"]["code"] <= 999:
                    logger.error(f"Request failed with code: {response_data['result']['code']}")
                    logger.error(f"Request failed with data: {response_data}")
                    current_retry += 1
                    continue

                return response_data
    logger.error(f"Request to {url} failed after {retry} retries.")
    raise RuntimeError(f"Request failed with code: {response_data['result']['code']}")
