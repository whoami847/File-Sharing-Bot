from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL, START_MSG
from helper_func import check_force_sub
from pyrogram.errors import ChatAdminRequired

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user

    # Check force subscription
    status = await check_force_sub(client, message)
    if status is False:
        try:
            link = await client.export_chat_invite_link(FORCE_SUB_CHANNEL)
        except ChatAdminRequired:
            await message.reply_text("Bot needs Invite via Link permission in the channel.")
            return
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            return

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Channel", url=link)],
             [InlineKeyboardButton("Try Again", callback_data="check_sub")]]
        )
        return await message.reply_text("Please join the channel to use this bot.", reply_markup=buttons)

    elif status is None:
        return await message.reply_text("Bot is not admin or channel ID is invalid.")

    # If already subscribed
    await message.reply_text(START_MSG)
