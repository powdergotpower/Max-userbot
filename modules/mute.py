from telethon import events, Button
from telethon.tl.types import ChatBannedRights
from telethon.errors import BadRequestError
from main import client  # Make sure client is imported from your main.py
from helpers.utils import get_user_from_event, _format

# Rights to mute normal users
MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True
)

# -----------------------------
# Smart mute command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.mute(?: |$)([\s\S]*)"))
async def mute(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return await event.reply("No user found to mute.")
    
    # Get participant info
    try:
        participant = await client.get_participants(event.chat_id, user_ids=[user.id])
        is_admin = participant[0].admin_rights or participant[0].creator
        is_owner = participant[0].creator
    except Exception:
        is_admin = False
        is_owner = False

    if is_owner:
        await event.reply(f"Sometimes [{user.first_name}](tg://user?id={user.id}) should stay quiet.")
    elif is_admin:
        await event.reply(f"Have some rest [{user.first_name}](tg://user?id={user.id}) admin.")
    else:
        # Normal user: restrict sending messages
        try:
            await client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
            await event.reply(f"Shhhh [{user.first_name}](tg://user?id={user.id}), stay muted for some time!")
        except BadRequestError:
            await event.reply("I don't have permission to mute this user.")

# -----------------------------
# Unmute command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.unmute(?: |$)([\s\S]*)"))
async def unmute(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return await event.reply("No user found to unmute.")

    try:
        from telethon.tl.functions.channels import EditBannedRequest
        from telethon.tl.types import ChatBannedRights

        UNMUTE_RIGHTS = ChatBannedRights(
            until_date=None,
            send_messages=None
        )
        await client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
        await event.reply(f"Unmuted [{user.first_name}](tg://user?id={user.id}) successfully.")
    except Exception:
        await event.reply("Failed to unmute this user.")

# -----------------------------
# Muteall command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.muteall"))
async def muteall(event):
    try:
        participants = await client.get_participants(event.chat_id)
        muted_count = 0
        for user in participants:
            if not user.admin_rights and not user.creator:
                await client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
                muted_count += 1
        await event.reply(f"Muted {muted_count} users (admins and owner untouched).")
    except Exception as e:
        await event.reply(f"Error while muting everyone: {e}")
