# (©)Codexbotz
import base64
import re
import asyncio
import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def is_subscribed(filter, client, update):
    """চেক করে ব্যবহারকারী চ্যানেলে সাবস্ক্রাইব করেছে কিনা।"""
    if not FORCE_SUB_CHANNEL:
        logger.info("No force subscription channel set.")
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        logger.info(f"User {user_id} is an admin, skipping subscription check.")
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
        logger.info(f"User {user_id} subscription status: {member.status}")
    except UserNotParticipant:
        logger.warning(f"User {user_id} is not a participant in channel {FORCE_SUB_CHANNEL}")
        return False

    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        logger.warning(f"User {user_id} is not an active member (status: {member.status})")
        return False
    return True

async def encode(string):
    """একটি স্ট্রিংকে বেস৬৪ ফরম্যাটে এনকোড করে।"""
    try:
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        base64_string = base64_bytes.decode("ascii").strip("=")
        logger.info(f"Encoded string: {base64_string}")
        return base64_string
    except Exception as e:
        logger.error(f"Error encoding string: {e}")
        raise

async def decode(base64_string):
    """বেস৬৪ স্ট্রিংকে ডিকোড করে।"""
    try:
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        string = string_bytes.decode("ascii")
        logger.info(f"Decoded string: {string}")
        return string
    except Exception as e:
        logger.error(f"Error decoding string: {e}")
        raise

async def get_messages(client, message_ids):
    """চ্যানেল থেকে একাধিক মেসেজ ফেচ করে।"""
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temp_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temp_ids
            )
            messages.extend(msgs)
        except FloodWait as e:
            logger.warning(f"FloodWait error, sleeping for {e.x} seconds")
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temp_ids
            )
            messages.extend(msgs)
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
        total_messages += len(temp_ids)
    logger.info(f"Fetched {len(messages)} messages")
    return messages

async def get_message_id(client, message):
    """মেসেজ থেকে আইডি বের করে।"""
    try:
        if message.forward_from_chat:
            if message.forward_from_chat.id == client.db_channel.id:
                return message.forward_from_message_id
            return 0
        elif message.forward_sender_name:
            return 0
        elif message.text:
            pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
            matches = re.match(pattern, message.text)
            if not matches:
                return 0
            channel_id, msg_id = matches.groups()
            if channel_id.isdigit():
                if f"-100{channel_id}" == str(client.db_channel.id):
                    return int(msg_id)
            else:
                if channel_id == client.db_channel.username.lstrip("@"):
                    return int(msg_id)
        return 0
    except Exception as e:
        logger.error(f"Error getting message ID: {e}")
        return 0

def get_readable_time(seconds: int) -> str:
    """সেকেন্ডকে পঠনযোগ্য সময়ে রূপান্তর করে।"""
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def delete_file(messages, client, process):
    """নির্দিষ্ট সময় পর মেসেজ মুছে ফেলে।"""
    await asyncio.sleep(AUTO_DELETE_TIME)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            logger.info(f"Deleted message {msg.id}")
        except FloodWait as e:
            logger.warning(f"FloodWait error while deleting message {msg.id}, sleeping for {e.x} seconds")
            await asyncio.sleep(e.x)
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            logger.error(f"Error deleting message {msg.id}: {e}")
    try:
        await process.edit_text(AUTO_DEL_SUCCESS_MSG)
        logger.info("Successfully edited process message with deletion success message")
    except Exception as e:
        logger.error(f"Error editing process message: {e}")

subscribed = filters.create(is_subscribed)
