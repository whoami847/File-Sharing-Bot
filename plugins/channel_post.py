# (©)Codexbotz
import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import encode, get_message_id, get_messages  # সংশোধিত আমদানি
from config import ADMINS, SOURCE_CODE, BOT_USERNAME, CUSTOM_CAPTION, AUTO_DELETE_TIME
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

@Client.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start', 'users', 'broadcast', 'genlink', 'stats', 'add_caption', 'remove_caption']))
async def channel_post(client: Client, message):
    try:
        message_id = await get_message_id(client, message)
        if message_id == 0:
            await message.reply("Invalid message or not forwarded from the database channel.")
            return
        
        post_link = f"https://t.me/{BOT_USERNAME}?start={await encode(f'{client.db_channel.id}_{message_id}')}"
        reply_text = f"Here is the shareable link for this post:\n\n{post_link}"

        if CUSTOM_CAPTION:
            reply_text += f"\n\n{CUSTOM_CAPTION}"

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f"https://t.me/share/url?url={post_link}")],
             [InlineKeyboardButton("🗑 Close", callback_data="close")]]
        )

        await message.reply(
            reply_text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

        if AUTO_DELETE_TIME:
            await asyncio.sleep(AUTO_DELETE_TIME)
            await message.delete()
            logger.info(f"Deleted message {message.id} after {AUTO_DELETE_TIME} seconds")
    except Exception as e:
        logger.error(f"Error in channel_post: {e}")
        await message.reply(f"An error occurred: {str(e)}")
