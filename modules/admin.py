from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest, EditPhotoRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, InputChatPhotoEmpty
from telethon.errors import BadRequestError, UserAdminInvalidError

# ---------------------
# Permission Rights
# ---------------------
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# ---------------------
# Register plugin
# ---------------------
def register(client):

    # Ban user
    @client.on(events.NewMessage(pattern=r"\.ban(?: |$)(.*)"))
    async def ban_user(event):
        if not event.is_group:
            return
        try:
            reply = await event.get_reply_message()
            user = reply.sender if reply else None
            if not user:
                await event.respond("Reply to a user to ban them.")
                return
            await client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
            await event.respond(f"🚫 Banned {user.first_name}")
        except UserAdminInvalidError:
            await event.respond("I need admin rights to ban users.")

    # Unban user
    @client.on(events.NewMessage(pattern=r"\.unban(?: |$)(.*)"))
    async def unban_user(event):
        if not event.is_group:
            return
        try:
            reply = await event.get_reply_message()
            user = reply.sender if reply else None
            if not user:
                await event.respond("Reply to a user to unban them.")
                return
            await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            await event.respond(f"✅ Unbanned {user.first_name}")
        except UserAdminInvalidError:
            await event.respond("I need admin rights to unban users.")

    # Kick user
    @client.on(events.NewMessage(pattern=r"\.kick(?: |$)(.*)"))
    async def kick_user(event):
        if not event.is_group:
            return
        try:
            reply = await event.get_reply_message()
            user = reply.sender if reply else None
            if not user:
                await event.respond("Reply to a user to kick them.")
                return
            await client.kick_participant(event.chat_id, user.id)
            await event.respond(f"👢 Kicked {user.first_name}")
        except UserAdminInvalidError:
            await event.respond("I need admin rights to kick users.")

    # Mute user
    @client.on(events.NewMessage(pattern=r"\.mute(?: |$)(.*)"))
    async def mute_user(event):
        if not event.is_group:
            return
        try:
            reply = await event.get_reply_message()
            user = reply.sender if reply else None
            if not user:
                await event.respond("Reply to a user to mute them.")
                return
            await client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
            await event.respond(f"🔇 Muted {user.first_name}")
        except UserAdminInvalidError:
            await event.respond("I need admin rights to mute users.")

    # Unmute user
    @client.on(events.NewMessage(pattern=r"\.unmute(?: |$)(.*)"))
    async def unmute_user(event):
        if not event.is_group:
            return
        try:
            reply = await event.get_reply_message()
            user = reply.sender if reply else None
            if not user:
                await event.respond("Reply to a user to unmute them.")
                return
            await client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
            await event.respond(f"🔊 Unmuted {user.first_name}")
        except UserAdminInvalidError:
            await event.respond("I need admin rights to unmute users.")

    # Pin message
    @client.on(events.NewMessage(pattern=r"\.pin(?: |$)(loud)?"))
    async def pin_message(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a message to pin.")
            return
        is_loud = bool(event.pattern_match.group(1))
        try:
            await client.pin_message(event.chat_id, reply.id, notify=is_loud)
            await event.respond(f"📌 Pinned message{' loudly' if is_loud else ''}.")
        except BadRequestError:
            await event.respond("I need admin rights to pin messages.")

    # Unpin message
    @client.on(events.NewMessage(pattern=r"\.unpin(?: |$)(all)?"))
    async def unpin_message(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        all_msgs = bool(event.pattern_match.group(1))
        try:
            if all_msgs:
                await client.unpin_message(event.chat_id)
                await event.respond("📌 Unpinned all messages.")
            elif reply:
                await client.unpin_message(event.chat_id, reply.id)
                await event.respond("📌 Message unpinned.")
            else:
                await event.respond("Reply to a message or use `.unpin all`.")
        except BadRequestError:
            await event.respond("I need admin rights to unpin messages.")

    # Purge messages
    @client.on(events.NewMessage(pattern=r"\.purge(?: |$)(\d+)?"))
    async def purge_messages(event):
        if not event.is_group:
            return
        try:
            limit = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 10
            msgs = await client.get_messages(event.chat_id, limit=limit)
            await client.delete_messages(event.chat_id, [m.id for m in msgs])
            await event.respond(f"🧹 Purged {len(msgs)} messages.")
        except Exception as e:
            await event.respond(f"Error: {e}")
