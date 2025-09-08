import aiohttp

from StealthIM import logger


async def ping(url: str) -> bool:
    """
    Ping the server to check if it is reachable.

    Args:
        url (str): The URL of the server to ping.

    Returns:
        bool: True if the server is reachable, False otherwise.
    """

    api_address = f"{url}/api/v1/ping"
    logger.debug(f"Called API ping with url: {api_address}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_address) as response:
                if response.status != 200:
                    logger.error(f"Ping failed with status: {response.status}")
                    return False
                response_data = await response.json()
        logger.debug(f"Response data: {response_data}")
        if response_data != {"message": "Hello, StealthIM!"}:
            return False
    except aiohttp.ClientError as e:
        logger.error(f"Ping failed with error: {e}")
        return False
    return True
