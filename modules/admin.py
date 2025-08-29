from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest, EditPhotoRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, InputChatPhotoEmpty
from telethon.errors import BadRequestError, UserAdminInvalidError, UserIdInvalidError, PhotoCropSizeSmallError, ImageProcessFailedError
from telethon.utils import get_display_name

# ======== GLOBAL RIGHTS ========
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)
UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None
)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# =================== ADMIN COMMANDS ===================
def register(client):

    @client.on(events.NewMessage(pattern=r"\.kick(?:\s|$)([\s\S]*)", outgoing=True))
    async def kick(event):
        reply = await event.get_reply_message()
        user_input = event.pattern_match.group(1).strip()
        if reply:
            user = reply.sender
        elif user_input:
            try:
                user = await client.get_entity(user_input)
            except Exception:
                return await event.respond("User not found")
        else:
            return await event.respond("Reply to a user or give a username/ID")

        try:
            await client.kick_participant(event.chat_id, user.id)
            await event.respond(f"Kicked [{user.first_name}](tg://user?id={user.id})!")
        except BadRequestError:
            await event.respond("I don't have permission to kick this user.")

    @client.on(events.NewMessage(pattern=r"\.ban(?:\s|$)([\s\S]*)", outgoing=True))
    async def ban(event):
        reply = await event.get_reply_message()
        user_input = event.pattern_match.group(1).strip()
        if reply:
            user = reply.sender
        elif user_input:
            try:
                user = await client.get_entity(user_input)
            except Exception:
                return await event.respond("User not found")
        else:
            return await event.respond("Reply to a user or give a username/ID")
        try:
            await client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
            await event.respond(f"Banned [{user.first_name}](tg://user?id={user.id})!")
        except BadRequestError:
            await event.respond("I don't have permission to ban this user.")

    @client.on(events.NewMessage(pattern=r"\.unban(?:\s|$)([\s\S]*)", outgoing=True))
    async def unban(event):
        reply = await event.get_reply_message()
        user_input = event.pattern_match.group(1).strip()
        if reply:
            user = reply.sender
        elif user_input:
            try:
                user = await client.get_entity(user_input)
            except Exception:
                return await event.respond("User not found")
        else:
            return await event.respond("Reply to a user or give a username/ID")
        try:
            await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            await event.respond(f"Unbanned [{user.first_name}](tg://user?id={user.id})!")
        except UserIdInvalidError:
            await event.respond("User is not banned.")

    @client.on(events.NewMessage(pattern=r"\.pin(?:\s|$)", outgoing=True))
    async def pin(event):
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a message to pin.")
        try:
            await client.pin_message(event.chat_id, reply.id)
            await event.respond("Pinned successfully!")
        except BadRequestError:
            await event.respond("I don't have permission to pin messages.")

    @client.on(events.NewMessage(pattern=r"\.unpin(?:\s|$)", outgoing=True))
    async def unpin(event):
        reply = await event.get_reply_message()
        try:
            if reply:
                await client.unpin_message(event.chat_id, reply.id)
            else:
                await client.unpin_message(event.chat_id)
            await event.respond("Unpinned successfully!")
        except BadRequestError:
            await event.respond("I don't have permission to unpin messages.")

    @client.on(events.NewMessage(pattern=r"\.clean(?:\s|$)(\d+)", outgoing=True))
    async def clean(event):
        limit = int(event.pattern_match.group(1))
        messages = await client.get_messages(event.chat_id, limit=limit)
        for msg in messages:
            try:
                await msg.delete()
            except Exception:
                pass
        await event.respond(f"Deleted last {limit} messages.")

    @client.on(events.NewMessage(pattern=r"\.mute(?:\s|$)([\s\S]*)", outgoing=True))
    async def mute(event):
        reply = await event.get_reply_message()
        user_input = event.pattern_match.group(1).strip()
        if reply:
            user = reply.sender
        elif user_input:
            try:
                user = await client.get_entity(user_input)
            except Exception:
                return await event.respond("User not found")
        else:
            return await event.respond("Reply to a user or give a username/ID")

        # Get chat participant info
        participant = await client.get_permissions(event.chat_id, user.id)
        if participant.is_owner:
            await event.respond(f"Sometimes [{user.first_name}](tg://user?id={user.id}) should stay quiet")
        elif participant.is_admin:
            await event.respond(f"Have some rest [{user.first_name}](tg://user?id={user.id}) admin, stay quiet")
        else:
            try:
                await client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
            except Exception:
                return await event.respond("Failed to mute user.")
            await event.respond(f"Shhhh [{user.first_name}](tg://user?id={user.id}) stay muted for some time")

    @client.on(events.NewMessage(pattern=r"\.unmute(?:\s|$)([\s\S]*)", outgoing=True))
    async def unmute(event):
        reply = await event.get_reply_message()
        user_input = event.pattern_match.group(1).strip()
        if reply:
            user = reply.sender
        elif user_input:
            try:
                user = await client.get_entity(user_input)
            except Exception:
                return await event.respond("User not found")
        else:
            return await event.respond("Reply to a user or give a username/ID")

        try:
            await client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
            await event.respond(f"Unmuted [{user.first_name}](tg://user?id={user.id})")
        except Exception:
            await event.respond("Failed to unmute user.")

    @client.on(events.NewMessage(pattern=r"\.muteall", outgoing=True))
    async def muteall(event):
        async for user in client.iter_participants(event.chat_id):
            perm = await client.get_permissions(event.chat_id, user.id)
            if not perm.is_admin and not perm.is_owner:
                try:
                    await client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
                except Exception:
                    pass
        await event.respond("All non-admins have been muted.")
