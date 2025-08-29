from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

def register(client):

    @client.on(events.NewMessage(pattern=r'\.owner'))
    async def owner_handler(event):
        chat = await event.get_chat()

        # Only work in groups or channels
        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        owner_mention = "Unavailable"

        try:
            if isinstance(chat, Channel):  # Supergroup / Channel
                full = await client(GetFullChannelRequest(chat.id))
                participants = full.full_chat.participants or []

                for p in participants:
                    try:
                        entity = await client.get_entity(p.user_id)
                        if getattr(p, "creator", False):
                            owner_mention = f"@{entity.username}" if entity.username else get_display_name(entity)
                            break
                    except Exception:
                        continue

            else:  # Basic Group
                full = await client(GetFullChatRequest(chat.id))
                for u in full.users:
                    entity = await client.get_entity(u.id)
                    if getattr(u, "creator", False) or getattr(u.admin_rights, "is_creator", False):
                        owner_mention = f"@{entity.username}" if entity.username else get_display_name(entity)
                        break

        except Exception as e:
            await event.reply(f"Failed to fetch owner: {e}")
            return

        await event.reply(f"👑 The group was created by: {owner_mention}")
