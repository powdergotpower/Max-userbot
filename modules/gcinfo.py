from telethon import events
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

daily_messages = {}

def register(client):

    @client.on(events.NewMessage(pattern=r'\.gcinfo'))
    async def gcinfo(event):
        chat = await event.get_chat()
        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        chat_id = chat.id

        # Total members
        try:
            members = await client.get_participants(chat)
            total_members = len(members)
        except:
            total_members = "Unknown"

        # Admins & owner
        admins = []
        owner = None
        try:
            async for m in client.iter_participants(chat, filter=lambda x: x.admin_rights or getattr(x, "creator", False)):
                if getattr(m, "creator", False):
                    owner = m
                else:
                    admins.append(m)
        except:
            pass

        admin_mentions = [f"@{a.username}" if a.username else get_display_name(a) for a in admins]
        owner_mention = f"@{owner.username}" if owner and owner.username else (owner.first_name if owner else "Unavailable")

        active_today = daily_messages.get(chat_id, 0)

        msg = (
            f"**Group Info:**\n"
            f"Title: {chat.title}\n"
            f"ID: `{chat_id}`\n"
            f"Total Members: {total_members}\n"
            f"Active Messages Today: {active_today}\n"
            f"Owner: {owner_mention}\n"
            f"Admins ({len(admin_mentions)}): {', '.join(admin_mentions)}"
        )

        await event.reply(msg)

    # Daily message counter
    @client.on(events.NewMessage)
    async def daily_counter(event):
        chat_id = event.chat_id
        daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1
