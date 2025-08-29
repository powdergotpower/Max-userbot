from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsAdmins
from telethon.utils import get_display_name

daily_messages = {}  # keeps track of messages per chat_id

def register(client):

    # Count every message for daily activity
    @client.on(events.NewMessage)
    async def daily_counter(event):
        chat_id = event.chat_id
        daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1

    # .gcinfo - Group Info
    @client.on(events.NewMessage(pattern=r'\.gcinfo'))
    async def gcinfo_handler(event):
        chat = await event.get_chat()

        # Only work in groups
        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        chat_title = chat.title
        chat_id = chat.id
        active_today = daily_messages.get(chat_id, 0)

        admins = []
        owner_mention = "Unavailable"
        total_members = 0

        try:
            if isinstance(chat, Channel):  # Supergroup/channel
                full = await client(GetFullChannelRequest(chat.id))
                total_members = full.full_chat.participants_count

                # Get admins (including owner)
                participants = await client(GetParticipantsRequest(
                    channel=chat,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=100,
                    hash=0
                ))

                for p in participants.users:
                    name = f"@{p.username}" if getattr(p, 'username', None) else get_display_name(p)
                    if getattr(p, 'creator', False):
                        owner_mention = name
                    else:
                        admins.append(name)

            else:  # Basic group
                full = await client(GetFullChatRequest(chat.id))
                total_members = len(full.users)

                for u in full.users:
                    name = f"@{u.username}" if getattr(u, 'username', None) else get_display_name(u)
                    if getattr(u, 'creator', False) or getattr(u.admin_rights, 'is_creator', False):
                        owner_mention = name
                    elif getattr(u, 'admin_rights', None):
                        admins.append(name)

        except Exception as e:
            await event.reply(f"Failed to fetch group info: {e}")
            return

        msg = (
            f"**Group Info:**\n"
            f"Title: {chat_title}\n"
            f"ID: `{chat_id}`\n"
            f"Total Members: {total_members}\n"
            f"Active Messages Today: {active_today}\n"
            f"Owner: {owner_mention}\n"
            f"Admins ({len(admins)}): {', '.join(admins) if admins else 'None'}"
        )

        await event.reply(msg)
