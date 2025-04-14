from config import FORCE_SUB_CHANNEL
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid
import logging

# লগিং সেটআপ করা
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_force_sub(client, message):
    if not FORCE_SUB_CHANNEL:
        logger.info("No force subscription channel set.")
        return True  # কোনো ফোর্স সাবস্ক্রিপশন চ্যানেল সেট করা নেই

    try:
        user_id = message.from_user.id
        logger.info(f"Checking subscription for user {user_id} in channel {FORCE_SUB_CHANNEL}")
        
        # চ্যানেলে ব্যবহারকারীর স্ট্যাটাস চেক করা
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)

        if member.status in ("kicked", "banned"):
            logger.warning(f"User {user_id} is banned from channel {FORCE_SUB_CHANNEL}")
            await message.reply_text("আপনি চ্যানেল থেকে ব্যান করা হয়েছেন। বট ব্যবহার করতে পারবেন না।")
            return False  # ব্যবহারকারী ব্যান করা

        logger.info(f"User {user_id} is a member of channel {FORCE_SUB_CHANNEL}")
        return True  # ব্যবহারকারী চ্যানেলের সদস্য

    except UserNotParticipant:
        logger.warning(f"User {user_id} is not a member of channel {FORCE_SUB_CHANNEL}")
        # ব্যবহারকারীকে চ্যানেলে জয়েন করার জন্য বলা
        await message.reply_text(
            f"এই বট ব্যবহার করতে আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে।\n"
            f"চ্যানেল: https://t.me/{FORCE_SUB_CHANNEL}\n"
            f"জয়েন করার পর আবার চেষ্টা করুন।"
        )
        return False  # ব্যবহারকারী সদস্য নন

    except (ChatAdminRequired, PeerIdInvalid) as e:
        logger.error(f"Bot error in channel {FORCE_SUB_CHANNEL}: {str(e)}")
        await message.reply_text(
            "বটের চ্যানেলে অ্যাডমিন অনুমতি নেই বা চ্যানেলের আইডি ভুল। "
            "দয়া করে বটের অ্যাডমিনের সাথে যোগাযোগ করুন।"
        )
        return None  # অ্যাডমিন অনুমতি নেই বা ভুল চ্যানেল আইডি
