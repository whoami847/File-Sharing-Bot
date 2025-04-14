from config import FORCE_SUB_CHANNEL
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid

async def check_force_sub(client, message):
    if not FORCE_SUB_CHANNEL:
        return True  # No force subscription required

    try:
        user_id = message.from_user.id
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        
        if member.status in ("kicked", "banned"):
            return False  # User is banned from the channel
        
        return True  # User is a member

    except UserNotParticipant:
        return False  # User is not a member

    except (ChatAdminRequired, PeerIdInvalid):
        print(f"[WARNING] - Bot doesn't have permission or wrong channel ID: {FORCE_SUB_CHANNEL}")
        return None  # Admin permission missing or invalid channel
