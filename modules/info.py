from telethon import events
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

import datetime

daily_messages = {}

def register(client):

    # .gcinfo - Group Info
    @client.on(events.NewMessage(pattern=r'\.gcinfo'))
    async def gcinfo_handler(event):
        chat = await event.get_chat()
        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        if isinstance(chat, Channel):
            full = await client(GetFullChannelRequest(chat.id))
            chat_title = full.chats[0].title
            members_count = full.full_chat.participants_count
            admins = [p.user_id for p in full.full_chat.admins]
            creator_id = None  # Creator not always directly accessible
        else:
            full = await client(GetFullChatRequest(chat.id))
            chat_title = full.chat.title
            members_count = len(full.users)
            admins = [u.id for u in full.users if u.admin_rights or u.creator]
            creator_id = None
            for u in full.users:
                if getattr(u, "creator", False) or getattr(u.admin_rights, "is_creator", False):
                    creator_id = u.id
                    break

        chat_id = chat.id
        active_today = daily_messages.get(chat_id, 0)

        admin_mentions = []
        for admin_id in admins:
            try:
                user = await client.get_entity(admin_id)
                admin_mentions.append(f"@{user.username}" if user.username else get_display_name(user))
            except Exception:
                continue

        creator_mention = "Unavailable"
        if creator_id:
            try:
                creator = await client.get_entity(creator_id)
                creator_mention = f"@{creator.username}" if creator.username else get_display_name(creator)
            except Exception:
                pass

        try:
            first_message = await client.get_messages(chat, limit=1, reverse=True)
            creation = first_message[0].date.strftime("%Y-%m-%d") if first_message else "Unknown"
        except Exception:
            creation = "Unknown"

        msg = (
            f"**Group Info:**\n"
            f"Title: {chat_title}\n"
            f"ID: `{chat_id}`\n"
            f"Total Members: {members_count}\n"
            f"Active Messages Today: {active_today}\n"
            f"Creator: {creator_mention}\n"
            f"Admins ({len(admin_mentions)}): {', '.join(admin_mentions)}\n"
            f"Creation Date (approx): {creation}"
        )
        await event.reply(msg)

    # .info - User Info
    @client.on(events.NewMessage(pattern=r'\.info(?: |$)(.*)'))
    async def info_handler(event):
        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
        elif arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use .info @username or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or use .info @username or .info user_id.")
            return

        full = await client(GetFullUserRequest(user.id))
        mutual_chats = len(await client.get_common_chats(user.id))

        last_name = user.last_name or ""
        username = user.username or "N/A"
        first_name = user.first_name or "N/A"

        status = "Unknown"
        if user.status:
            try:
                if hasattr(user.status, "was_online") and user.status.was_online:
                    status = f"Last seen at {user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
                elif hasattr(user.status, "online") and user.status.online:
                    status = "Online now"
                else:
                    status = f"{user.status.__class__.__name__}"
            except Exception:
                status = "Unknown"

        msg = (
            f"**User Info:**\n"
            f"Name: {first_name} {last_name}\n"
            f"ID: `{user.id}`\n"
            f"Username: @{username}\n"
            f"Last Seen: {status}\n"
            f"Mutual Groups: {mutual_chats}"
        )
        await event.reply(msg)

    # Daily message count tracker
    @client.on(events.NewMessage)
    async def daily_counter(event):
        chat_id = event.chat_id
        daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1
