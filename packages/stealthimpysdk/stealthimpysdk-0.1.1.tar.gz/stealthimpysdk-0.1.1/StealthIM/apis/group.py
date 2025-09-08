import dataclasses
import enum

from StealthIM import logger
from .common import request, Result, NoValResult


@dataclasses.dataclass
class GetGroupsResult:
    groups: list[int]
    result: Result


class GroupMemberType(enum.Enum):
    Member = 0
    Manager = 1
    Owner = 2


@dataclasses.dataclass
class GroupMember:
    name: str
    type: GroupMemberType


@dataclasses.dataclass
class GroupInfoResult:
    members: list[GroupMember]
    result: Result


@dataclasses.dataclass
class GroupPublicInfoResult:
    create_at: str
    name: str
    result: Result


@dataclasses.dataclass
class CreateGroupResult:
    groupid: int
    result: Result


JoinGroupResult = NoValResult
InviteGroupResult = NoValResult
SetMemberRoleResult = NoValResult
KickMemberResult = NoValResult
ChangeGroupNameResult = NoValResult
ChangeGroupPasswordResult = NoValResult


async def get_groups(
        url: str,
        session: str,
) -> GetGroupsResult:
    api_address = f"{url}/api/v1/group/"
    logger.debug(f"Called API get_groups with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }

    response_data = await request(api_address, "GET", headers=header)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return GetGroupsResult(
        groups=response_data["groups"] if success else None,
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def get_group_info(
        url: str,
        session: str,
        groupid: int,
):
    api_address = f"{url}/api/v1/group/{groupid}"
    logger.debug(f"Called API get_group_info with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }

    response_data = await request(api_address, "GET", headers=header)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return GroupInfoResult(
        members=[
            GroupMember(
                name=member["name"],
                type=GroupMemberType(member.get("type", 0)),
            ) for member in response_data["members"]
        ] if success else None,
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def get_group_public_info(
        url: str,
        session: str,
        groupid: int,
) -> GroupPublicInfoResult:
    api_address = f"{url}/api/v1/group/{groupid}/public"
    logger.debug(f"Called API get_group_public_info with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }

    response_data = await request(api_address, "GET", headers=header)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return GroupPublicInfoResult(
        create_at=response_data["create_at"] if success else None,
        name=response_data["name"] if success else None,
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def create_group(
        url: str,
        session: str,
        group_name: str,
) -> CreateGroupResult:
    api_address = f"{url}/api/v1/group"
    logger.debug(f"Called API create_group with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "name": group_name,
    }

    response_data = await request(api_address, "POST", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    success = response_data["result"]["code"] == 800

    return CreateGroupResult(
        groupid=response_data["groupid"] if success else None,
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def join_group(
        url: str,
        session: str,
        groupid: int,
        password: str,
) -> JoinGroupResult:
    api_address = f"{url}/api/v1/group/{groupid}/join"
    logger.debug(f"Called API join_group with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "password": password,
    }

    response_data = await request(api_address, "POST", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    return JoinGroupResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def invite_group(
        url: str,
        session: str,
        groupid: int,
        username: str,
) -> InviteGroupResult:
    api_address = f"{url}/api/v1/group/{groupid}/invite"
    logger.debug(f"Called API invite_group with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "username": username,
    }

    response_data = await request(api_address, "POST", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    return InviteGroupResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def set_user_role(
        url: str,
        session: str,
        groupid: int,
        username: str,
        user_type: GroupMemberType,
) -> SetMemberRoleResult:
    api_address = f"{url}/api/v1/group/{groupid}/{username}"
    logger.debug(f"Called API set_user_type with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "type": user_type.value,
    }

    response_data = await request(api_address, "PUT", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    return SetMemberRoleResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def kick_user(
        url: str,
        session: str,
        groupid: int,
        username: str,
) -> KickMemberResult:
    api_address = f"{url}/api/v1/group/{groupid}/{username}"
    logger.debug(f"Called API kick_user with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }

    response_data = await request(api_address, "DELETE", headers=header)
    logger.debug(f"Response data: {response_data}")

    return KickMemberResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def change_group_name(
        url: str,
        session: str,
        groupid: int,
        name: str,
) -> ChangeGroupNameResult:
    api_address = f"{url}/api/v1/group/{groupid}/name"
    logger.debug(f"Called API change_group_name with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "name": name,
    }

    response_data = await request(api_address, "PATCH", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    return ChangeGroupNameResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def change_group_password(
        url: str,
        session: str,
        groupid: int,
        password: str,
) -> ChangeGroupPasswordResult:
    api_address = f"{url}/api/v1/group/{groupid}/password"
    logger.debug(f"Called API change_group_password with url: {api_address}")
    header = {
        "Authorization": f"Bearer {session}"
    }
    body = {
        "password": password,
    }

    response_data = await request(api_address, "PATCH", headers=header, body=body)
    logger.debug(f"Response data: {response_data}")

    return ChangeGroupPasswordResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )
