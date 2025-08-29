from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights
from datetime import datetime, timedelta

# Global storage for counting messages
daily_messages = {}

# Default rights
BANNED_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

def register(client):

    # ---------------- PIN ----------------
    @client.on(events.NewMessage(pattern=r'^\.pin( loud|$)', outgoing=True))
    async def pin_msg(event):
        if not event.is_group:
            return
        to_pin = event.reply_to_msg_id
        if not to_pin:
            return await event.respond("Reply to a message to pin it.")
        is_silent = bool(event.pattern_match.group(1))
        await client.pin_message(event.chat_id, to_pin, notify=not is_silent)
        await event.respond("Pinned successfully!")

    # ---------------- UNPIN ----------------
    @client.on(events.NewMessage(pattern=r'^\.unpin( all|$)', outgoing=True))
    async def unpin_msg(event):
        if not event.is_group:
            return
        to_unpin = event.reply_to_msg_id
        options = (event.pattern_match.group(1) or "").strip()
        if not to_unpin and options != "all":
            return await event.respond("Reply to a message to unpin or use `.unpin all`.")
        if to_unpin and not options:
            await client.unpin_message(event.chat_id, to_unpin)
        else:
            await client.unpin_message(event.chat_id)
        await event.respond("Unpinned successfully!")

    # ---------------- BAN ----------------
    @client.on(events.NewMessage(pattern=r'^\.ban(?:\s|$)', outgoing=True))
    async def ban(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a user to ban them.")
        user = reply.sender
        await client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
        await event.respond(f"Banned [{user.first_name}](tg://user?id={user.id})")

    # ---------------- UNBAN ----------------
    @client.on(events.NewMessage(pattern=r'^\.unban(?:\s|$)', outgoing=True))
    async def unban(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a user to unban them.")
        user = reply.sender
        await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await event.respond(f"Unbanned [{user.first_name}](tg://user?id={user.id})")

    # ---------------- KICK ----------------
    @client.on(events.NewMessage(pattern=r'^\.kick(?:\s|$)', outgoing=True))
    async def kick(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a user to kick them.")
        user = reply.sender
        await client.kick_participant(event.chat_id, user.id)
        await event.respond(f"Kicked [{user.first_name}](tg://user?id={user.id})")

    # ---------------- PROMOTE ----------------
    @client.on(events.NewMessage(pattern=r'^\.promote(?:\s|$)([\s\S]*)', outgoing=True))
    async def promote(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a user to promote them.")
        user = reply.sender
        title = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else "Admin"
        new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False,
                                     ban_users=True, delete_messages=True, pin_messages=True)
        await client(EditAdminRequest(event.chat_id, user.id, new_rights, title))
        await event.respond(f"Promoted [{user.first_name}](tg://user?id={user.id}) as {title}")

    # ---------------- DEMOTE ----------------
    @client.on(events.NewMessage(pattern=r'^\.demote(?:\s|$)', outgoing=True))
    async def demote(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("Reply to a user to demote them.")
        user = reply.sender
        new_rights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None,
                                     ban_users=None, delete_messages=None, pin_messages=None)
        await client(EditAdminRequest(event.chat_id, user.id, new_rights, "Member"))
        await event.respond(f"Demoted [{user.first_name}](tg://user?id={user.id})")

    # ---------------- GCINFO ----------------
    @client.on(events.NewMessage(pattern=r'^\.gcinfo$', outgoing=True))
    async def gcinfo(event):
        if not event.is_group:
            return
        chat = await client.get_chat(event.chat_id)
        full = await client(GetFullChannelRequest(event.chat_id))
        admins = [u.user for u in full.full_chat.admins if hasattr(u, 'user')]
        owner = full.full_chat.creator
        members_count = full.full_chat.participants_count
        bots = len([m for m in full.full_chat.participants if getattr(m, 'bot', False)])
        pinned_msg = full.full_chat.pinned_msg_id
        description = full.full_chat.about or "No description"
        creation = getattr(full.full_chat, 'date', None)

        # Active and daily messages
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

        msg = f"**GC INFO:**\n"
        msg += f"Name: {chat.title}\n"
        msg += f"ID: {chat.id}\n"
        msg += f"Owner: [{owner.first_name}](tg://user?id={owner.id})\n"
        msg += f"Admins ({len(admins)}): " + ", ".join(f"[{a.first_name}](tg://user?id={a.id})" for a in admins[:10]) + "\n"
        msg += f"Members: {members_count}\nActive (24h): {len(active_members)}\nDaily Messages: {daily_count}\nBots: {bots}\n"
        msg += f"Pinned Msg ID: {pinned_msg}\nDescription: {description}\nType: {'Supergroup' if getattr(chat, 'megagroup', False) else 'Basic group'}\n"
        if creation:
            msg += f"Created on: {creation.strftime('%Y-%m-%d %H:%M:%S')}\n"
        await event.respond(msg)

    # ---------------- MESSAGE COUNTER ----------------
    @client.on(events.NewMessage(incoming=True))
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
