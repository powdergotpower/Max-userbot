from telethon import events
from telethon.tl.functions.channels import GetFullChannel
from telethon.tl.functions.users import GetFullUser
from telethon.tl.types import ChannelParticipantsAdmins, UserStatusOffline, UserStatusOnline
from datetime import datetime

# Track daily messages (simple in-memory counter)
DAILY_MSGS = {}

def get_daily_msgs(chat_id, user_id):
    return DAILY_MSGS.get(chat_id, {}).get(user_id, 0)

@client.on(events.NewMessage(pattern=r'\.gcinfo'))
async def gcinfo(event):
    chat = await event.get_chat()
    try:
        full = await client(GetFullChannel(channel=chat.id))
    except:
        await event.reply("Cannot fetch full info for this chat.")
        return

    participants = await client.get_participants(chat.id)
    admins = [p for p in participants if getattr(p.participant, 'admin_rights', None) or getattr(p.participant, 'creator', False)]
    total_users = len(participants)

    # Active members today
    active_users = len([uid for uid, msgs in DAILY_MSGS.get(chat.id, {}).items() if msgs > 0])
    
    owner = None
    for a in admins:
        if getattr(a.participant, 'creator', False):
            owner = a
            break

    # Total daily messages in this group
    group_daily_msgs = sum(DAILY_MSGS.get(chat.id, {}).values())

    # Description
    description = getattr(full.full_chat, 'about', None) or getattr(full.full_chat, 'description', 'No description')

    # Invite link
    invite_link = getattr(full.full_chat, 'exported_invite', None) or 'No invite link'

    msg = f"**Group Info:**\n"
    msg += f"Title: {chat.title}\n"
    msg += f"ID: {chat.id}\n"
    msg += f"Description: {description}\n"
    msg += f"Invite link: {invite_link}\n"
    msg += f"Total members: {total_users}\n"
    msg += f"Admins count: {len(admins)}\n"
    msg += f"Active members today: {active_users}\n"
    msg += f"Daily messages today: {group_daily_msgs}\n"
    if owner:
        msg += f"Owner: [{owner.first_name}](tg://user?id={owner.id})\n"

    await event.reply(msg)


@client.on(events.NewMessage(pattern=r'\.info(?: |$)(.*)'))
async def user_info(event):
    if event.is_reply:
        user = (await event.get_reply_message()).sender
    else:
        args = event.pattern_match.group(1)
        if not args:
            await event.reply("Reply to a user or provide a username/ID.")
            return
        user = await client.get_entity(args)

    full = await client(GetFullUser(user.id))

    # Count common groups
    common_chats = await client.get_common_chats(user.id)
    total_common = len(common_chats)

    # Daily messages in groups we share
    daily_msgs = sum([get_daily_msgs(chat.id, user.id) for chat in common_chats])

    # Last seen / online status
    if isinstance(user.status, UserStatusOnline):
        status = "Online"
    elif isinstance(user.status, UserStatusOffline):
        last_seen = user.status.was_online.strftime("%Y-%m-%d %H:%M")
        status = f"Last seen: {last_seen}"
    else:
        status = "Status unknown"

    msg = f"**User Info:**\n"
    msg += f"Name: {user.first_name} {user.last_name or ''}\n"
    msg += f"Username: @{user.username or 'N/A'}\n"
    msg += f"ID: {user.id}\n"
    msg += f"Total common groups: {total_common}\n"
    msg += f"Daily messages today: {daily_msgs}\n"
    msg += f"Status: {status}\n"

    # Roles in common groups
    roles = []
    for chat in common_chats:
        participants = await client.get_participants(chat.id, filter=ChannelParticipantsAdmins)
        if any(p.id == user.id for p in participants):
            roles.append(f"{chat.title} (Admin)")
        else:
            roles.append(f"{chat.title} (Member)")
    if roles:
        msg += "Roles in common groups:\n" + "\n".join(roles[:10])  # limit to 10 groups

    await event.reply(msg)
