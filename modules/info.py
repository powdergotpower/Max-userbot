# modules/info.py
from telethon import events
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Channel, Chat

import datetime

# Store daily message count per chat
daily_messages = {}

# -----------------------------
# .gcinfo - Group info
# -----------------------------
@client.on(events.NewMessage(pattern=r'\.gcinfo'))
async def gcinfo_handler(event):
    chat = await event.get_chat()

    # Determine type of chat
    if isinstance(chat, Channel):
        full = await client(GetFullChannelRequest(chat.id))
        chat_title = full.chats[0].title
        members_count = full.full_chat.participants_count
        admins = [p.user_id for p in full.full_chat.admins]
        creator_id = full.chats[0].creator
    elif isinstance(chat, Chat):
        full = await client(GetFullChatRequest(chat.id))
        chat_title = full.chat.title
        members_count = len(full.users)
        admins = [u.id for u in full.users if getattr(u, 'bot', False) is False and getattr(u, 'admin_rights', None)]
        creator_id = full.chat.admins[0].user_id if full.chat.admins else None
    else:
        await event.reply("Unable to fetch group info.")
        return

    chat_id = chat.id
    active_users = daily_messages.get(chat_id, 0)

    msg = f"**Group Info:**\n" \
          f"Title: {chat_title}\n" \
          f"ID: `{chat_id}`\n" \
          f"Total Members: {members_count}\n" \
          f"Active Today: {active_users}\n" \
          f"Admins Count: {len(admins)}\n" \
          f"Creator ID: `{creator_id}`"

    await event.reply(msg)

# -----------------------------
# .info - User info
# -----------------------------
@client.on(events.NewMessage(pattern=r'\.info(?: |$)(.*)'))
async def info_handler(event):
    arg = event.pattern_match.group(1)
    if event.is_reply and not arg:
        user = await event.get_reply_message().get_sender()
    elif arg:
        try:
            if arg.isdigit():
                user = await client.get_entity(int(arg))
            elif arg.startswith("@"):
                user = await client.get_entity(arg)
            else:
                await event.reply("Invalid input, use @username or reply to a user.")
                return
        except:
            await event.reply("User not found.")
            return
    else:
        await event.reply("Reply to a user or provide a username.")
        return

    full = await client(GetFullUserRequest(user.id))

    mutual_chats = len(await client.get_common_chats(user.id))
    last_name = user.last_name or "N/A"
    username = user.username or "N/A"

    msg = f"**User Info:**\n" \
          f"Name: {user.first_name} {last_name}\n" \
          f"ID: `{user.id}`\n" \
          f"Username: @{username}\n" \
          f"Mutual Groups: {mutual_chats}"

    await event.reply(msg)

# -----------------------------
# Count messages for daily activity
# -----------------------------
@client.on(events.NewMessage)
async def daily_counter(event):
    chat_id = event.chat_id
    daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1
