from typing import TYPE_CHECKING

import StealthIM
from .apis.common import NoValResult
from .apis.group import GetGroupsResult
from .apis.user import (
    UserInfo, UserPublicInfo, ChangePasswordResult, ChangePhoneNumberResult, ChangeNicknameResult, ChangeEmailResult,
    DeleteResult
)

if TYPE_CHECKING:
    from .server import Server


def not_deleted(func):
    def inner(self, *args, **kwargs):
        if self.deleted:
            raise RuntimeError('User was already deleted')
        return func(self, *args, **kwargs)
    return inner


class User:
    def __init__(self, server: "Server", session: str):
        self.server = server
        self.session = session
        self.deleted = False

    @not_deleted
    async def get_self_info(self) -> UserInfo:
        """
        Get self information of the user.

        Returns:
            UserInfo: The information of the user.

        Raises:
            RuntimeError: If the user is deleted.
        """
        return await StealthIM.apis.user.get_self_info(self.server.url, self.session)

    @not_deleted
    async def get_user_info(self, username: str) -> UserPublicInfo:
        """
        Get public information of a user by username.

        Args:
            username (str): The username of the user to get information for.

        Returns:
            UserPublicInfo: The public information of the user.

        Raises:
            RuntimeError: If the user is deleted or the request fails.
        """
        return await StealthIM.apis.user.get_user_info(self.server.url, self.session, username)

    @not_deleted
    async def change_password(self, new_password: str) -> ChangePasswordResult:
        """
        Change the user's password.

        Args:
            new_password (str): The new password to set for the user.

        Returns:
            ChangePasswordResult: The result of the password change operation.

        Raises:
            RuntimeError: If the password change fails or the user is deleted.
        """
        return await StealthIM.apis.user.change_password(self.server.url, self.session, new_password)

    @not_deleted
    async def change_email(self, new_email: str) -> ChangeEmailResult:
        """
        Change the user's email.

        Args:
            new_email (str): The new email to set for the user.

        Returns:
            ChangePasswordResult: The result of the email change operation.

        Raises:
            RuntimeError: If the email change fails or the user is deleted.
        """
        return await StealthIM.apis.user.change_email(self.server.url, self.session, new_email)

    @not_deleted
    async def change_nickname(self, new_nickname: str) -> ChangeNicknameResult:
        """
        Change the user's nickname.

        Args:
            new_nickname (str): The new nickname to set for the user.

        Returns:
            ChangePasswordResult: The result of the nickname change operation.

        Raises:
            RuntimeError: If the nickname change fails or the user is deleted.
        """
        return await StealthIM.apis.user.change_nickname(self.server.url, self.session, new_nickname)

    @not_deleted
    async def change_phone_number(self, new_phone_number: str) -> ChangePhoneNumberResult:
        """
        Change the user's phone number.

        Args:
            new_phone_number (str): The new phone number to set for the user.

        Returns:
            ChangePasswordResult: The result of the phone number change operation.

        Raises:
            RuntimeError: If the phone number change fails or the user is deleted.
        """
        return await StealthIM.apis.user.change_phone_number(self.server.url, self.session, new_phone_number)

    @not_deleted
    async def update_info(
            self,
            password: str = None,
            email: str = None,
            nickname: str = None,
            phone_number: str = None
    ) -> NoValResult:
        """
        Update the user's information.

        Args:
            password (str, optional): The new password to set for the user. Defaults to None.
            email (str, optional): The new email to set for the user. Defaults to None.
            nickname (str, optional): The new nickname to set for the user. Defaults to None.
            phone_number (str, optional): The new phone number to set for the user. Defaults to None.

        Returns:
            NoValResult: The result of the update operation.

        Raises:
            RuntimeError: If the update fails or if the user is deleted.
        """
        if not any([password, email, nickname, phone_number]):
            raise ValueError("At least one of password, email, nickname, or phone_number must be provided.")
        if password:
            result = await self.change_password(password)
            if result.result.code != 800:
                raise RuntimeError(f"Password change failed with code {result.result.code}")
        if email:
            result = await self.change_email(email)
            if result.result.code != 800:
                raise RuntimeError(f"Email change failed with code {result.result.code}")
        if nickname:
            result = await self.change_nickname(nickname)
            if result.result.code != 800:
                raise RuntimeError(f"Nickname change failed with code {result.result.code}")
        if phone_number:
            result = await self.change_phone_number(phone_number)
            if result.result.code != 800:
                raise RuntimeError(f"Phone number change failed with code {result.result.code}")
        return NoValResult(
            result=StealthIM.apis.common.Result(code=800, msg="")
        )

    async def delete(self) -> DeleteResult:
        """
        Delete the user.

        Returns:
            DeleteResult: The result of the delete operation.

        Raises:
            RuntimeError: If the delete fails.
        """
        res = await StealthIM.apis.user.delete(self.server.url, self.session)
        if res.result.code == 800:
            self.deleted = True
        return res

    @not_deleted
    async def get_groups(self) -> GetGroupsResult:
        """
        Get all groups.

        Returns:
            GetGroupsResult: The result of the get groups operation.
        """
        return await StealthIM.apis.group.get_groups(self.server.url, self.session)
