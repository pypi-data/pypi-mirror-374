import logging
import re
import asyncio
import nonebot
import httpx
from nonebot import on_request
from nonebot import on_command
from nonebot.rule import Rule
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupRequestEvent
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Bot
from motor.motor_asyncio import AsyncIOMotorClient

__plugin_meta__ = PluginMetadata(
    name='KIRAKIRA☆DOUGA入群验证',
    type='application',
    description='KIRAKIRA☆DOUGA入群验证！',
    homepage='https://github.com/NekoooDesu/nonebot-plugin-okashi',
    usage="通过判断用户入群提供的信息，通过 KiRAKiRA-Rosales 提供的 API 查询用户名验证入群",
    config={},
    extra={}
)

join_group = on_request(
    priority=1,
    block=True
)

change_card = on_command(
    '改名片',
    rule=to_me(),
    priority=5,
    block=True
)

async def get_username(uid: str) -> str:
    user_api = f'https://rosales.kirakira.moe/user/info?uid={uid}'
    async with httpx.AsyncClient() as client:
        resp = await client.get(user_api)
        data = resp.json()
        if data.get("success"):
            result = data.get("result", {})
            nickname = result.get("userNickname")
            if nickname:
                return nickname
            return result.get("username", "")
        return None

async def check_comment(uid: str, invitation_code: str) -> bool:
    config = nonebot.get_driver().config
    uuid = getattr(config, "uuid", None)
    token = getattr(config, "token", None)
    logging.info(f"收到入群验证请求，uid={uid}, invitation_code={invitation_code}")
    if not uuid or not token:
        logging.error("uuid 或 token 未配置")
        return False
    verify_api = f'https://rosales.kirakira.moe/user/getUserByInvitationCode?invitationCode={invitation_code}'
    cookies = {"uuid": uuid, "token": token}
    async with httpx.AsyncClient() as client:
        resp = await client.get(verify_api, cookies=cookies)
        data = resp.json()
        logging.debug(f"后端返回数据: {data}")
        if data.get("success") and "userInfoResult" in data:
            result = str(data["userInfoResult"].get("uid")) == uid
            logging.info(f"验证结果: {result}")
            return result
        logging.warning("后端返回失败或缺少 userInfoResult")
        return False

@join_group.handle()
async def _grh(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == 'add':
        comment = event.comment.strip().splitlines()[-1]
        match = re.search(r"(\d+)\s+([A-Za-z0-9\-]+)", event.comment)
        if match:
            uid, invitation_code = match.groups()
            if await check_comment(uid, invitation_code):
                await event.approve(bot)
                await asyncio.sleep(2)
                username = await get_username(uid)
                
                if username:
                    await bot.set_group_card(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        card=f"{username} UID{uid} "
                    )
                else:
                    await bot.set_group_card(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        card=f"{uid}"
                    )
                
                logging.info(f"<UNK>{uid}<UNK>{invitation_code}<UNK>")
                #await join_group.finish(MessageSegment.at(event.user_id) + f'\n欢迎加入群聊!\n请注意遵守群规，愉快地玩耍吧！')
            else:
                logging.info(f'认证失败，uid={uid}, invitation_code={invitation_code}')
                #await event.reject(bot)
        else:
            logging.info(f'格式错误，comment={comment}')
            #await event.reject(bot)

expect_list= [
    "2854196310",
    "3889024489",
    "573455496"
]

async def get_group_members(bot: Bot, group_id: int):
    resp = await bot.call_api("get_group_member_list", group_id=group_id)
    return resp

async def update_group_card(bot: Bot, group_id: int, user_id: int, card: str):
    await bot.set_group_card(group_id=group_id, user_id=user_id, card=card)

async def save_to_mongodb(uid: str, qq: int, group_id: int):
    config = nonebot.get_driver().config
    MONGO_URI = getattr(config, "MONGO_URI", None)
    DB_NAME = getattr(config, "DB_NAME", None)
    COLLECTION_NAME = getattr(config, "COLLECTION_NAME", None)
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[COLLECTION_NAME]
    await coll.update_one(
        {"uid": uid, "qq": qq, "group_id": group_id},
        {"$set": {"uid": uid, "qq": qq, "group_id": group_id}},
        upsert=True
    )
    client.close()

async def is_admin(user_id: str) -> bool:
    config = nonebot.get_driver().config
    admin_ids = getattr(config, "superusers", [])
    if str(user_id) in admin_ids:
        return True
    else: 
        return False

@change_card.handle()
async def _cc(bot: Bot, event: PrivateMessageEvent, args: Message = CommandArg()):
    logging.info(f"收到改名片请求，参数: {args}")
    group_id = None


    await bot.send(event, "正在处理，请稍候...")
    try:
        group_id = int(str(args).strip())
    except Exception:
        await change_card.finish("请提供正确的群号，格式: /改名片 群号")
        return

    members = await get_group_members(bot, group_id)
    await bot.send(event, f"获取到 {len(members)} 名群成员，正在处理名片...")

    for member in members:
        user_id = member["user_id"]
        if str(user_id) in expect_list:
            logging.info(f"跳过白名单用户 {user_id}")
            continue
        card = member.get("card", "")
        nickname = member.get("nickname", "")
        match = re.match(r"(.+)\sUID(\d+)", card)
        if match:
            name, uid = match.groups()
            username = await get_username(uid)
            if username:
                new_card = f"{username} (UID:{uid})"
            else:
                new_card = f"UID:{uid}"
            await update_group_card(bot, group_id, user_id, new_card)
            await save_to_mongodb(uid, user_id, group_id)
        else:
            # 尝试从名片或昵称中提取 UID
            uid_match = re.search(r"UID(\d+)", card) or re.search(r"UID(\d+)", nickname)
            uid = uid_match.group(1) if uid_match else None
            if uid:
                # 只改名片，不发消息
                await update_group_card(bot, group_id, user_id, f"UID:{uid}")
                await save_to_mongodb(uid, user_id, group_id)
                logging.info(f"已为用户 {user_id} 补全名片为 UID:{uid}")
            else:
                try:
                    await bot.send_private_msg(user_id=event.user_id, message=f"你的群名片({user_id})格式不正确，请修改为“名字 (UID:XXX)”")
                except Exception:
                    logging.warning(f"无法向 {event.user_id} 发送私信")
    await change_card.finish(f"群 {group_id} 名片已处理完成")