from config import FORCE_SUB_CHANNEL
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid

async def check_force_sub(client, message):
    if not FORCE_SUB_CHANNEL:
        return True  # No force sub needed
    
    try:
        user_id = message.from_user.id
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ("kicked", "banned"):
            return False
        return True
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, PeerIdInvalid):
        print(f"[WARNING] - Bot doesn't have permission or wrong channel ID: {FORCE_SUB_CHANNEL}")
        return None
