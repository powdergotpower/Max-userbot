from telethon import events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsAdmins
from telethon.utils import get_display_name

def register(client):

    @client.on(events.NewMessage(pattern=r'\.owner'))
    async def owner_handler(event):
        chat = await event.get_chat()
        owner_mention = "Unavailable"

        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        try:
            if isinstance(chat, Channel):
                participants = await client(GetParticipantsRequest(
                    channel=chat,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=100,
                    hash=0
                ))

                # Try to find the real creator
                owner_entity = None
                for p in participants.users:
                    if getattr(p, "creator", False):
                        owner_entity = await client.get_entity(p.id)
                        break

                # Fallback: first admin as owner
                if not owner_entity and participants.users:
                    owner_entity = await client.get_entity(participants.users[0].id)

                if owner_entity:
                    owner_mention = f"@{owner_entity.username}" if owner_entity.username else get_display_name(owner_entity)

            else:  # Basic group
                full = await client(GetFullChatRequest(chat.id))
                for u in full.users:
                    if getattr(u, "creator", False) or getattr(u.admin_rights, "is_creator", False):
                        owner_entity = await client.get_entity(u.id)
                        owner_mention = f"@{owner_entity.username}" if owner_entity.username else get_display_name(owner_entity)
                        break

        except Exception as e:
            await event.reply(f"Failed to fetch owner: {e}")
            return

        await event.reply(f"👑 The group was created by: {owner_mention}")
