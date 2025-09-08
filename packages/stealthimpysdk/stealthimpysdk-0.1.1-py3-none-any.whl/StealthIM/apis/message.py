import dataclasses
import enum
import json
from typing import Optional

import aiohttp

from .common import request, NoValResult, Result
from .. import logger


class MessageType(enum.Enum):
    Text = 0
    Image = 1
    LargeEmoji = 2
    Emoji = 3
    File = 4
    Card = 5
    InnerLink = 6
    Recall = 16


SendMessageResult = NoValResult
RecallMessageResult = NoValResult


@dataclasses.dataclass
class Message:
    groupid: int
    msg: str
    msgid: str
    time: str
    type: MessageType
    username: str
    hash: Optional[str] = None


async def send_message(
        url: str,
        session: str,
        groupid: int,
        message: str,
        message_type: MessageType,
) -> SendMessageResult:
    api_address = f'{url}/api/v1/message/{groupid}'
    logger.debug(f"Called API send_message with url {api_address}")
    headers = {
        "Authorization": f"Bearer {session}",
    }
    body = {
        "msg": message,
        "type": message_type.value,
    }

    response_data = await request(api_address, "POST", body=body, headers=headers)
    logger.debug(f"Response data: {response_data}")

    return SendMessageResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def recall_message(
        url: str,
        session: str,
        groupid: int,
        message_id: int
) -> RecallMessageResult:
    api_address = f'{url}/api/v1/message/{groupid}'
    logger.debug(f"Called API recall_message with url {api_address}")
    headers = {
        "Authorization": f"Bearer {session}",
    }
    body = {
        "msgid": message_id,
    }

    response_data = await request(api_address, "PATCH", body=body, headers=headers)
    logger.debug(f"Response data: {response_data}")

    return RecallMessageResult(
        result=Result(
            code=response_data["result"]["code"],
            msg=response_data["result"]["msg"]
        )
    )


async def get_message(
        url: str,
        session: str,
        groupid: int,
        from_id: int,
        direction: int
):
    # noinspection PyStatementEffect
    direction  # currently unused

    api_address = f'{url}/api/v1/message/{groupid}?msgid={from_id}'
    logger.debug(f"Called API get_message with url {api_address}")
    headers = {
        "Authorization": f"Bearer {session}",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(api_address) as response:
            if response.status != 200:
                raise RuntimeError(f"Request failed with status: {response.status}")

            async for line in response.content:
                # 解码成字符串
                line = line.decode('utf-8').strip()
                if line.startswith('data:'):
                    # 提取消息内容
                    message = line[len('data:'):].strip()

                    data = json.loads(message)
                    logger.debug(f"Response data: {data}")
                    if data["result"]["code"] != 800:
                        raise RuntimeError(f"Request failed with code: {data['result']['code']}")
                    for msg in data["msg"]:
                        yield Message(
                            groupid=msg["groupid"],
                            msg=msg["msg"],
                            msgid=msg["msgid"],
                            time=msg["time"],
                            type=MessageType(msg["type"]),
                            username=msg["username"],
                            hash=msg.get("hash", None),
                        )
