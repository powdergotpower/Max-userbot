from telethon import events
from telethon.errors.rpcerrorlist import (BadRequestError, UserAdminInvalidError, UserIdInvalidError)
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights, InputChatPhotoEmpty
from telethon.utils import get_display_name

# ============== Rights settings ===============
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
    view_messages=None,
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

def register(client):

    # Ban command
    @client.on(events.NewMessage(pattern=r"\.ban( .*)?", outgoing=True))
    async def ban_user(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to ban them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
            await event.reply(f"Banned {get_display_name(user)}.")
        except BadRequestError:
            await event.reply("Insufficient permissions to ban.")

    # Unban command
    @client.on(events.NewMessage(pattern=r"\.unban( .*)?", outgoing=True))
    async def unban_user(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to unban them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            await event.reply(f"Unbanned {get_display_name(user)}.")
        except BadRequestError:
            await event.reply("Insufficient permissions to unban.")

    # Mute
    @client.on(events.NewMessage(pattern=r"\.mute( .*)?", outgoing=True))
    async def mute_user(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to mute them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
            await event.reply(f"Muted {get_display_name(user)}.")
        except BadRequestError:
            await event.reply("Insufficient permissions to mute.")

    # Unmute
    @client.on(events.NewMessage(pattern=r"\.unmute( .*)?", outgoing=True))
    async def unmute_user(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to unmute them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
            await event.reply(f"Unmuted {get_display_name(user)}.")
        except BadRequestError:
            await event.reply("Insufficient permissions to unmute.")

    # Promote to admin
    @client.on(events.NewMessage(pattern=r"\.promote( .*)?", outgoing=True))
    async def promote(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to promote them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        rights = ChatAdminRights(
            add_admins=False,
            invite_users=True,
            change_info=True,
            ban_users=True,
            delete_messages=True,
            pin_messages=True,
        )
        try:
            await event.client(EditAdminRequest(event.chat_id, user.id, rights, "Admin"))
            await event.reply(f"Promoted {get_display_name(user)} to admin.")
        except BadRequestError:
            await event.reply("Insufficient permissions to promote.")

    # Demote from admin
    @client.on(events.NewMessage(pattern=r"\.demote( .*)?", outgoing=True))
    async def demote(event):
        if not event.is_group:
            await event.reply("❌ This command can only be used in groups.")
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.reply("Reply to a user's message to demote them.")
            return
        user = await event.client.get_entity(reply.sender_id)
        rights = ChatAdminRights()
        try:
            await event.client(EditAdminRequest(event.chat_id, user.id, rights, "Member"))
            await event.reply(f"Demoted {get_display_name(user)} from admin.")
        except BadRequestError:
            await event.reply("Insufficient permissions to demote.")
