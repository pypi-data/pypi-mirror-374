from typing import Optional

from StealthIM.apis import user, util
from StealthIM.apis.user import RegisterResult
from StealthIM.user import User


class Server:
    def __init__(self, url: str):
        """
        Initialize the Server instance with the given URL.

        Args:
            url (str): The URL of the StealthIM server.

        Raises:
            ValueError: If the server is not reachable.
        """
        self.url = url.rstrip('/')

    async def ping(self):
        """
        Check if the server is reachable by sending a ping request.

        Returns:
            bool: True if the server is reachable, False otherwise.
        """
        return await util.ping(self.url)

    async def register(
            self,
            username: str,
            password: str,
            nickname: str,
            email: str = None,
            phone_number: str = None
    ) -> RegisterResult:
        """
        Register a new user on the server.

        Args:
            username (str): The username of the new user.
            password (str): The password of the new user.
            nickname (str): The nickname of the new user.
            email (str, optional): The email of the new user. Defaults to None.
            phone_number (str, optional): The phone number of the new user. Defaults to None.

        Returns:
            RegisterResult: The result of the registration.

        Raises:
            RuntimeError: If the registration fails for any reason.
        """
        return await user.register(self.url, username, password, nickname, email, phone_number)

    async def login(
            self,
            username: str,
            password: str
    ) -> Optional[User]:
        """
        Log in to the server with the given username and password.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            Optional[User]: An instance of User if login is successful, None if the user does
                not exist or the password is incorrect.
        Raises:
            RuntimeError: If the login fails for any other reason.
        """
        login_data = await user.login(self.url, username, password)
        if login_data.result.code in (1201, 1203):
            return None
        if login_data.result.code != 800:
            raise RuntimeError(f"Login failed with code {login_data.result.code}")

        return User(self, login_data.session)

    def _login_from_session(
            self,
            session: str
    ) -> User:
        """
        Create a User instance from an existing session.

        Args:
            session (str): The session string.

        Returns:
            User: An instance of User with the given session.
        """
        return User(self, session)
