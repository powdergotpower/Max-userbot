from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights
from datetime import datetime, timedelta

from userbot import catub

plugin_category = "admin"

# Simple in-memory storage for daily messages
daily_messages = {}

# ========== PIN / UNPIN ==========
@catub.cat_cmd(pattern=r"pin( loud|$)", command=("pin", plugin_category), groups_only=True, require_admin=True)
async def pin_msg(event):
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await event.reply("Reply to a message to pin it.")
    is_silent = bool(event.pattern_match.group(1))
    await event.client.pin_message(event.chat_id, to_pin, notify=not is_silent)
    await event.reply("Pinned successfully!")

@catub.cat_cmd(pattern=r"unpin( all|$)", command=("unpin", plugin_category), groups_only=True, require_admin=True)
async def unpin_msg(event):
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    if not to_unpin and options != "all":
        return await event.reply("Reply to a message to unpin or use `.unpin all`.")
    if to_unpin and not options:
        await event.client.unpin_message(event.chat_id, to_unpin)
    else:
        await event.client.unpin_message(event.chat_id)
    await event.reply("Unpinned successfully!")

# ========== BAN / UNBAN ==========
BANNED_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

@catub.cat_cmd(pattern=r"ban(?:\s|$)([\s\S]*)", command=("ban", plugin_category), groups_only=True, require_admin=True)
async def ban_user(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a user to ban.")
    user = await event.get_sender()
    await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    await event.reply(f"Banned {user.first_name}.")

@catub.cat_cmd(pattern=r"unban(?:\s|$)([\s\S]*)", command=("unban", plugin_category), groups_only=True, require_admin=True)
async def unban_user(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a user to unban.")
    user = await event.get_sender()
    await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
    await event.reply(f"Unbanned {user.first_name}.")

# ========== KICK ==========
@catub.cat_cmd(pattern=r"kick(?:\s|$)", command=("kick", plugin_category), groups_only=True, require_admin=True)
async def kick_user(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a user to kick.")
    user = await event.get_sender()
    await event.client.kick_participant(event.chat_id, user.id)
    await event.reply(f"Kicked {user.first_name}.")

# ========== PROMOTE / DEMOTE ==========
@catub.cat_cmd(pattern=r"promote(?:\s|$)", command=("promote", plugin_category), groups_only=True, require_admin=True)
async def promote_user(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a user to promote.")
    user = await event.get_sender()
    new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False, ban_users=True, delete_messages=True, pin_messages=True)
    await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, "Admin"))
    await event.reply(f"Promoted {user.first_name}.")

@catub.cat_cmd(pattern=r"demote(?:\s|$)", command=("demote", plugin_category), groups_only=True, require_admin=True)
async def demote_user(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a user to demote.")
    user = await event.get_sender()
    new_rights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None, ban_users=None, delete_messages=None, pin_messages=None)
    await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, "Member"))
    await event.reply(f"Demoted {user.first_name}.")

# ========== GCINFO ==========
@catub.cat_cmd(pattern=r"gcinfo", command=("gcinfo", plugin_category), groups_only=True)
async def gcinfo(event):
    chat = await event.get_chat()
    full = await event.client(GetFullChannelRequest(event.chat_id))
    admins = [u.user for u in full.full_chat.admins if hasattr(u, 'user')]
    owner = full.full_chat.creator
    members_count = full.full_chat.participants_count
    bots = len([m for m in full.full_chat.participants if getattr(m, 'bot', False)])
    
    # Active members and daily messages
    now = datetime.utcnow()
    since = now - timedelta(days=1)
    chat_id = event.chat_id
    daily_count = 0
    active_members = set()
    if chat_id in daily_messages:
        for uid, times in daily_messages[chat_id].items():
            daily_count += len([t for t in times if t > since])
            if any(t > since for t in times):
                active_members.add(uid)

    msg = f"**GC INFO:**\nName: {chat.title}\nID: {chat.id}\nOwner: [{owner.first_name}](tg://user?id={owner.id})\nAdmins ({len(admins)}): "
    msg += ", ".join(f"[{a.first_name}](tg://user?id={a.id})" for a in admins[:10])
    msg += f"\nMembers: {members_count}\nActive (24h): {len(active_members)}\nDaily Messages: {daily_count}\nBots: {bots}\nType: {'Supergroup' if getattr(chat, 'megagroup', False) else 'Basic group'}"
    await event.reply(msg)

# ========== WATCHER TO COUNT DAILY MESSAGES ==========
@catub.cat_cmd(incoming=True)
async def count_messages(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    user_id = event.sender_id
    now = datetime.utcnow()
    if chat_id not in daily_messages:
        daily_messages[chat_id] = {}
    if user_id not in daily_messages[chat_id]:
        daily_messages[chat_id][user_id] = []
    daily_messages[chat_id][user_id].append(now)
