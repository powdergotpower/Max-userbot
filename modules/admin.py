from telethon import events
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.types import ChatAdminRights, ChatBannedRights, InputChatPhotoEmpty
from telethon.errors import BadRequestError, UserAdminInvalidError, UserIdInvalidError

from ..core.managers import edit_or_reply, edit_delete
from ..helpers.utils import get_user_from_event, _format
from ..core.data import _sudousers_list
from ..core.logger import logging
from . import BOTLOG, BOTLOG_CHATID

LOGS = logging.getLogger(__name__)

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

# ------------------- ADMIN COMMANDS -------------------

@catub.cat_cmd(pattern=r"promote(?:\s|$)([\s\S]*)", groups_only=True, require_admin=True)
async def promote(event):
    user, rank = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "`User not found.`")
    if not rank:
        rank = "Admin"
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )
    catevent = await edit_or_reply(event, "`Promoting...`")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await catevent.edit("`I don't have permission to promote!`")
    await catevent.edit(f"`{user.first_name} promoted successfully!`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#PROMOTE\nUSER: [{user.first_name}](tg://user?id={user.id})\nCHAT: {event.chat_id}",
        )


@catub.cat_cmd(pattern=r"demote(?:\s|$)([\s\S]*)", groups_only=True, require_admin=True)
async def demote(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "`User not found.`")
    new_rights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    catevent = await edit_or_reply(event, "`Demoting...`")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, "admin"))
    except BadRequestError:
        return await catevent.edit("`I don't have permission to demote!`")
    await catevent.edit(f"`{user.first_name} demoted successfully!`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#DEMOTE\nUSER: [{user.first_name}](tg://user?id={user.id})\nCHAT: {event.chat_id}",
        )


@catub.cat_cmd(pattern=r"ban(?:\s|$)([\s\S]*)", groups_only=True, require_admin=True)
async def ban(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "`User not found.`")
    
    # Prevent banning admins/owner
    participant = await event.client.get_permissions(event.chat_id, user.id)
    if participant.admin_rights or participant.creator:
        return await edit_or_reply(event, "`Cannot ban an admin or owner!`")
    
    catevent = await edit_or_reply(event, "`Banning...`")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await catevent.edit("`I don't have permission to ban!`")
    
    await catevent.edit(f"`{user.first_name} is banned! Reason: {reason or 'No reason'}`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#BAN\nUSER: [{user.first_name}](tg://user?id={user.id})\nCHAT: {event.chat_id}\nREASON: {reason or 'No reason'}",
        )


@catub.cat_cmd(pattern=r"unban(?:\s|$)([\s\S]*)", groups_only=True, require_admin=True)
async def unban(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "`User not found.`")
    
    catevent = await edit_or_reply(event, "`Unbanning...`")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
    except UserIdInvalidError:
        return await catevent.edit("`Cannot unban this user.`")
    except Exception as e:
        return await catevent.edit(f"**Error:** {e}")
    
    await catevent.edit(f"`{user.first_name} is unbanned successfully.`")


@catub.cat_cmd(pattern=r"kick(?:\s|$)([\s\S]*)", groups_only=True, require_admin=True)
async def kick(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "`User not found.`")
    
    # Prevent kicking admins/owner
    participant = await event.client.get_permissions(event.chat_id, user.id)
    if participant.admin_rights or participant.creator:
        return await edit_or_reply(event, "`Cannot kick an admin or owner!`")
    
    catevent = await edit_or_reply(event, "`Kicking...`")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except BadRequestError:
        return await catevent.edit("`I don't have permission to kick!`")
    
    await catevent.edit(f"`{user.first_name} has been kicked! Reason: {reason or 'No reason'}`")


@catub.cat_cmd(pattern=r"pin( loud|$)", groups_only=True, require_admin=True)
async def pin(event):
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await edit_delete(event, "`Reply to a message to pin.`")
    is_silent = bool(event.pattern_match.group(1))
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await edit_delete(event, "`I don't have permission to pin.`")
    await edit_delete(event, "`Message pinned successfully!`", 3)


@catub.cat_cmd(pattern=r"unpin( all|$)", groups_only=True, require_admin=True)
async def unpin(event):
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1) or "").strip()
    try:
        if options == "all":
            await event.client.unpin_message(event.chat_id)
        elif to_unpin:
            await event.client.unpin_message(event.chat_id, to_unpin)
        else:
            return await edit_delete(event, "`Reply to a message to unpin or use .unpin all.`")
    except BadRequestError:
        return await edit_delete(event, "`I don't have permission to unpin.`")
    await edit_delete(event, "`Message unpinned successfully!`", 3)
