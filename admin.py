from telethon.tl import functions
from telethon.tl.types import ChatAdminRights, ChatBannedRights
from userbot import catub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event
from . import BOTLOG, BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
plugin_category = "admin"

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


@catub.cat_cmd(pattern=r"promote(?:\s|$)([\s\S]*)", command=("promote", plugin_category), groups_only=True, require_admin=True)
async def promote(event):
    "Promote a user to admin"
    user, rank = await get_user_from_event(event)
    if not user:
        return
    if not rank:
        rank = "Admin"
    catevent = await edit_or_reply(event, "`Promoting...`")
    new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False, ban_users=True, delete_messages=True, pin_messages=True)
    try:
        await event.client(functions.channels.EditAdminRequest(event.chat_id, user.id, new_rights, rank))
        await catevent.edit("✅ Promoted successfully!")
        if BOTLOG:
            await event.client.send_message(BOTLOG_CHATID, f"#PROMOTE\nUser: [{user.first_name}](tg://user?id={user.id})\nChat: {await event.get_chat()}")
    except Exception as e:
        await catevent.edit(f"❌ Error: {e}")


@catub.cat_cmd(pattern=r"demote(?:\s|$)([\s\S]*)", command=("demote", plugin_category), groups_only=True, require_admin=True)
async def demote(event):
    "Demote a user from admin"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`Demoting...`")
    newrights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None, ban_users=None, delete_messages=None, pin_messages=None)
    try:
        await event.client(functions.channels.EditAdminRequest(event.chat_id, user.id, newrights, "admin"))
        await catevent.edit("✅ Demoted successfully!")
    except Exception as e:
        await catevent.edit(f"❌ Error: {e}")


@catub.cat_cmd(pattern=r"ban(?:\s|$)([\s\S]*)", command=("ban", plugin_category), groups_only=True, require_admin=True)
async def ban_user(event):
    "Ban a user from group"
    user, reason = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`Banning...`")
    try:
        await event.client(functions.channels.EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
        if reason:
            await catevent.edit(f"✅ Banned [{user.first_name}](tg://user?id={user.id})\nReason: {reason}")
        else:
            await catevent.edit(f"✅ Banned [{user.first_name}](tg://user?id={user.id})")
    except Exception as e:
        await catevent.edit(f"❌ Error: {e}")


@catub.cat_cmd(pattern=r"unban(?:\s|$)([\s\S]*)", command=("unban", plugin_category), groups_only=True, require_admin=True)
async def unban_user(event):
    "Unban a user from group"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`Unbanning...`")
    try:
        await event.client(functions.channels.EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await catevent.edit(f"✅ Unbanned [{user.first_name}](tg://user?id={user.id}) successfully!")
    except Exception as e:
        await catevent.edit(f"❌ Error: {e}")


@catub.cat_cmd(pattern=r"kick(?:\s|$)([\s\S]*)", command=("kick", plugin_category), groups_only=True, require_admin=True)
async def kick_user(event):
    "Kick a user from group"
    user, reason = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`Kicking...`")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
        if reason:
            await catevent.edit(f"✅ Kicked [{user.first_name}](tg://user?id={user.id})\nReason: {reason}")
        else:
            await catevent.edit(f"✅ Kicked [{user.first_name}](tg://user?id={user.id})")
    except Exception as e:
        await catevent.edit(f"❌ Error: {e}")
