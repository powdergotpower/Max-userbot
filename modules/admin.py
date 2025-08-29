from telethon import events
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
from telethon.tl.functions.channels import EditBannedRequest
from telethon.utils import get_display_name
from datetime import datetime, timedelta

plugin_category = "admin"

# Banned / muted rights
BAN_RIGHTS = ChatBannedRights(
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
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

def register(client):

    # ------------------- BAN -------------------
    @client.on(events.NewMessage(pattern=r"\.ban", outgoing=True))
    async def ban_user(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a user to ban.")
            return
        await event.client(EditBannedRequest(event.chat_id, reply.sender_id, BAN_RIGHTS))
        await event.respond(f"🚫 User {reply.sender_id} banned!")

    # ------------------- UNBAN -------------------
    @client.on(events.NewMessage(pattern=r"\.unban", outgoing=True))
    async def unban_user(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a user to unban.")
            return
        await event.client(EditBannedRequest(event.chat_id, reply.sender_id, UNBAN_RIGHTS))
        await event.respond(f"✅ User {reply.sender_id} unbanned!")

    # ------------------- MUTE -------------------
    @client.on(events.NewMessage(pattern=r"\.mute", outgoing=True))
    async def mute_user(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a user to mute.")
            return
        await event.client(EditBannedRequest(event.chat_id, reply.sender_id, MUTE_RIGHTS))
        await event.respond(f"🔇 User {reply.sender_id} muted!")

    # ------------------- UNMUTE -------------------
    @client.on(events.NewMessage(pattern=r"\.unmute", outgoing=True))
    async def unmute_user(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a user to unmute.")
            return
        await event.client(EditBannedRequest(event.chat_id, reply.sender_id, UNMUTE_RIGHTS))
        await event.respond(f"🔊 User {reply.sender_id} unmuted!")

    # ------------------- KICK -------------------
    @client.on(events.NewMessage(pattern=r"\.kick", outgoing=True))
    async def kick_user(event):
        if not event.is_group:
            return
        reply = await event.get_reply_message()
        if not reply:
            await event.respond("Reply to a user to kick.")
            return
        await event.client.kick_participant(event.chat_id, reply.sender_id)
        await event.respond(f"👢 User {reply.sender_id} kicked!")

    # ------------------- PIN -------------------
    @client.on(events.NewMessage(pattern=r"\.pin( loud)?", outgoing=True))
    async def pin_message(event):
        if not event.is_group:
            return
        reply_id = event.reply_to_msg_id
        if not reply_id:
            await event.respond("Reply to a message to pin.")
            return
        loud = bool(event.pattern_match.group(1))
        await event.client.pin_message(event.chat_id, reply_id, notify=loud)
        await event.respond("📌 Message pinned!")

    # ------------------- UNPIN -------------------
    @client.on(events.NewMessage(pattern=r"\.unpin( all)?", outgoing=True))
    async def unpin_message(event):
        if not event.is_group:
            return
        all_msgs = bool(event.pattern_match.group(1))
        if all_msgs:
            await event.client.unpin_message(event.chat_id)
            await event.respond("📌 All messages unpinned!")
        else:
            reply_id = event.reply_to_msg_id
            if not reply_id:
                await event.respond("Reply to a message to unpin.")
                return
            await event.client.unpin_message(event.chat_id, reply_id)
            await event.respond("📌 Message unpinned!")

    # ------------------- GCINFO -------------------
    @client.on(events.NewMessage(pattern=r"\.gcinfo", outgoing=True))
    async def group_info(event):
        if not event.is_group:
            return
        chat = await event.get_chat()
        participants = await event.client.get_participants(event.chat_id)
        admins = await event.client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins)
        owner = next((a for a in admins if getattr(a.participant, "creator", False)), None)

        active_members = [p for p in participants if p.status and getattr(p.status, "was_online", None)]
        daily_msgs = "N/A"  # Placeholder: real daily count requires logging

        text = (
            f"📊 **Group Info:**\n"
            f"**Title:** {chat.title}\n"
            f"**ID:** {event.chat_id}\n"
            f"**Members:** {len(participants)}\n"
            f"**Active Members:** {len(active_members)}\n"
            f"**Admins:** {len(admins)}\n"
            f"**Owner:** {get_display_name(owner) if owner else 'Unknown'}\n"
            f"**Daily Messages:** {daily_msgs}"
        )
        await event.respond(text)
