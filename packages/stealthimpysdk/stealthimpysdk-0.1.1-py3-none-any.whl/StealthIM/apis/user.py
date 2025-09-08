import dataclasses
from typing import Optional

from StealthIM import logger
from .common import Result, request, NoValResult

RegisterResult = NoValResult


@dataclasses.dataclass
class UserInfo:
    result: Result
    create_time: str
    email: str
    nickname: str
    phone_number: str
    username: str


@dataclasses.dataclass
class LoginResult:
    result: Result
    session: Optional[str] = None
    user_info: Optional[UserInfo] = None


@dataclasses.dataclass
class UserPublicInfo:
    result: Result
    nickname: str


ChangePasswordResult = NoValResult
ChangeEmailResult = NoValResult
ChangeNicknameResult = NoValResult
ChangePhoneNumberResult = NoValResult
DeleteResult = NoValResult


async def register(
        url: str,
        username: str,
        password: str,
        nickname: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None
) -> RegisterResult:
    """
    Register a new user.

    Args:
        url (str): The URL of the server.
        username (str): The username of the new user.
        password (str): The password of the new user.
        nickname (str): The nickname of the new user.
        email (Optional[str]): The email of the new user.
        phone_number (Optional[str]): The phone number of the new user.

    Returns:
        RegisterResult: The result of the registration.
    """
    api_address = f"{url}/api/v1/user/register"
    logger.debug(f"Called API register with url: {api_address}")
    email = email if email else ""
    phone_number = phone_number if phone_number else ""
    body = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "email": email,
        "phone_number": phone_number
    }

    response_data = await request(api_address, "POST", body=body)
    logger.debug(f"Response data: {response_data}")

    return RegisterResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def login(
        url: str,
        username: str,
        password: str
) -> LoginResult:
    """
    Log in a user.

    Args:
        url (str): The URL of the server.
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        LoginResult: The result of the login.
    """
    api_address = f"{url}/api/v1/user"
    logger.debug(f"Called API login with url: {api_address}")
    data = {
        "username": username,
        "password": password
    }
    response_data = await request(api_address, "POST", body=data)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return LoginResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        ),
        session=response_data["session"] if success else None,
        user_info=UserInfo(
            result=Result(
                code=800,
                msg=""
            ),
            create_time=response_data["user_info"]["create_time"],
            email=response_data["user_info"]["email"],
            nickname=response_data["user_info"]["nickname"],
            phone_number=response_data["user_info"]["phone_number"],
            username=response_data["user_info"]["username"]
        ) if success else None
    )


async def get_self_info(
        url: str,
        session: str
) -> UserInfo:
    """
    Get self information.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.

    Returns:
        UserInfo: The information of the user.
    """
    api_address = f"{url}/api/v1/user"
    logger.debug(f"Called API self_info with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    response_data = await request(api_address, "GET", headers=header)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return UserInfo(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        ),
        create_time=response_data["user_info"]["create_time"] if success else None,
        email=response_data["user_info"]["email"] if success else None,
        nickname=response_data["user_info"]["nickname"] if success else None,
        phone_number=response_data["user_info"]["phone_number"] if success else None,
        username=response_data["user_info"]["username"] if success else None
    )


async def get_user_info(
        url: str,
        session: str,
        username: str
) -> UserPublicInfo:
    """
    Get user information.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.
        username (str): The username of the user to get information for.

    Returns:
        UserInfo: The information of the user.
    """
    api_address = f"{url}/api/v1/user/{username}"
    logger.debug(f"Called API user_info with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    response_data = await request(api_address, "GET", headers=header)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return UserPublicInfo(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        ),
        nickname=response_data["user_info"]["nickname"] if success else None
    )


async def change_password(
        url: str,
        session: str,
        password: str,
) -> ChangePasswordResult:
    """
    Change the password of the user.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.
        password (str): The new password.

    Returns:
        ChangePasswordResult: The result of the password change.
    """
    api_address = f"{url}/api/v1/user/password"
    logger.debug(f"Called API change_password with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "password": password
    }
    response_data = await request(api_address, "PATCH", body=body, headers=header)
    logger.debug(f"Response data: {response_data}")

    return ChangePasswordResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def change_email(
        url: str,
        session: str,
        email: str
) -> ChangeEmailResult:
    """
    Change the email of the user.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.
        email (str): The new email.

    Returns:
        ChangeEmailResult: The result of the email change.
    """
    api_address = f"{url}/api/v1/user/email"
    logger.debug(f"Called API change_email with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "email": email
    }
    response_data = await request(api_address, "PATCH", body=body, headers=header)
    logger.debug(f"Response data: {response_data}")

    return ChangeEmailResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def change_nickname(
        url: str,
        session: str,
        nickname: str
) -> ChangeNicknameResult:
    """
    Change the nickname of the user.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.
        nickname (str): The new nickname.

    Returns:
        ChangeNicknameResult: The result of the nickname change.
    """
    api_address = f"{url}/api/v1/user/nickname"
    logger.debug(f"Called API change_nickname with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "nickname": nickname
    }
    response_data = await request(api_address, "PATCH", body=body, headers=header)
    logger.debug(f"Response data: {response_data}")

    return ChangeNicknameResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def change_phone_number(
        url: str,
        session: str,
        phone_number: str
) -> ChangePhoneNumberResult:
    """
    Change the phone number of the user.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.
        phone_number (str): The new phone number.

    Returns:
        ChangePhoneNumberResult: The result of the phone number change.
    """
    api_address = f"{url}/api/v1/user/phone"
    logger.debug(f"Called API change_phone_number with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "phone_number": phone_number
    }
    response_data = await request(api_address, "PATCH", body=body, headers=header)
    logger.debug(f"Response data: {response_data}")

    return ChangePhoneNumberResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def delete(
        url: str,
        session: str
) -> DeleteResult:
    """
    Delete the user.

    Args:
        url (str): The URL of the server.
        session (str): The session token of the user.

    Returns:
        LogoutResult: The result of the delete operation.
    """
    api_address = f"{url}/api/v1/user"
    logger.debug(f"Called API delete with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    response_data = await request(api_address, "DELETE", headers=header)
    logger.debug(f"Response data: {response_data}")

    return DeleteResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )
