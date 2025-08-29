# modules/info.py
from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChannelParticipantsAdmins
from datetime import datetime
import asyncio

# -------------------------
# Daily messages storage
# -------------------------
daily_messages = {}  # {chat_id: {user_id: count}}

def track_message(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    if chat_id not in daily_messages:
        daily_messages[chat_id] = {}
    if user_id not in daily_messages[chat_id]:
        daily_messages[chat_id][user_id] = 0
    daily_messages[chat_id][user_id] += 1

# -------------------------
# Group info command
# -------------------------
@events.register(events.NewMessage(pattern=r'\.gcinfo'))
async def gcinfo(event):
    if not event.is_group:
        await event.reply("This command works only in groups.")
        return

    chat = await event.get_chat()
    full_chat = await event.client(GetFullChannelRequest(chat))
    owner = None
    admins_list = []

    # get owner and admins
    for participant in full_chat.full_chat.participants.participants:
        if hasattr(participant, 'participant'):
            if getattr(participant.participant, 'admin_rights', None):
                admins_list.append(participant)
        if getattr(participant.participant, 'user_id', None) == full_chat.full_chat.creator:
            owner = participant

    total_members = chat.participants_count
    active_members = len(daily_messages.get(chat.id, {}))
    bot_count = len([u for u in full_chat.full_chat.participants.participants if u.user_id < 0])

    msg = f"**Group Info:**\n"
    msg += f"Name: {chat.title}\n"
    msg += f"ID: `{chat.id}`\n"
    msg += f"Owner: {owner.user_id if owner else 'Unknown'}\n"
    msg += f"Admins: {', '.join(str(a.user_id) for a in admins_list) if admins_list else 'None'}\n"
    msg += f"Total members: {total_members}\n"
    msg += f"Active members today: {active_members}\n"
    msg += f"Number of bots: {bot_count}\n"
    msg += f"Daily messages count: {sum(daily_messages.get(chat.id, {}).values())}\n"
    msg += f"Created at: {chat.date if hasattr(chat, 'date') else 'Unknown'}\n"
    
    await event.reply(msg)

# -------------------------
# User info command
# -------------------------
@events.register(events.NewMessage(pattern=r'\.info(?:\s+|$)(.*)'))
async def user_info(event):
    await track_message(event)  # Track messages for activity

    args = event.pattern_match.group(1).strip()
    if args:
        # Try to get user by username
        try:
            user = await event.client.get_entity(args)
        except Exception:
            await event.reply("User not found.")
            return
    elif event.is_reply:
        reply = await event.get_reply_message()
        user = await event.client.get_entity(reply.sender_id)
    else:
        user = await event.client.get_entity(event.sender_id)

    full_user = await event.client(GetFullUserRequest(user.id))
    common_chats = await event.client.get_common_chats(user.id)

    user_daily = 0
    for chat_id, data in daily_messages.items():
        if user.id in data:
            user_daily += data[user.id]

    msg = f"**User Info:**\n"
    msg += f"Name: {user.first_name or ''} {user.last_name or ''}\n"
    msg += f"Username: @{user.username if user.username else 'None'}\n"
    msg += f"ID: `{user.id}`\n"
    msg += f"Bot: {'Yes' if user.bot else 'No'}\n"
    msg += f"Common groups with you: {len(common_chats)}\n"
    msg += f"Daily messages count: {user_daily}\n"
    msg += f"About: {full_user.about or 'No bio'}\n"
    
    await event.reply(msg)
