from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsAdmins
from telethon.utils import get_display_name

daily_messages = {}

def register(client):

    # Daily message counter
    @client.on(events.NewMessage)
    async def daily_counter(event):
        chat_id = event.chat_id
        daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1

    @client.on(events.NewMessage(pattern=r'\.gcinfo'))
    async def gcinfo_handler(event):
        chat = await event.get_chat()
        chat_id = chat.id
        active_today = daily_messages.get(chat_id, 0)

        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        chat_title = chat.title
        total_members = 0
        owner_mention = "Unavailable"
        admins = []

        try:
            if isinstance(chat, Channel):
                full = await client(GetFullChannelRequest(chat.id))
                total_members = full.full_chat.participants_count

                participants = await client(GetParticipantsRequest(
                    channel=chat,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=100,
                    hash=0
                ))

                # Find owner by checking for 'creator' flag or highest permissions
                owner_entity = None
                potential_admins = []

                for p in participants.users:
                    entity = await client.get_entity(p.id)
                    mention = f"[{get_display_name(entity)}](tg://user?id={entity.id})"
                    
                    # Telegram does not always set creator flag; check permission level
                    is_creator = getattr(p, 'creator', False)
                    if is_creator:
                        owner_entity = entity
                    else:
                        potential_admins.append((entity, mention))

                # Fallback if no creator found: choose admin with full permissions or first admin
                if owner_entity is None and potential_admins:
                    owner_entity = potential_admins[0][0]
                    owner_mention = potential_admins[0][1]
                    admins = [m[1] for m in potential_admins[1:]]
                elif owner_entity:
                    owner_mention = f"[{get_display_name(owner_entity)}](tg://user?id={owner_entity.id})"
                    admins = [m[1] for m in potential_admins]
                else:
                    owner_mention = "Unavailable"
                    admins = []

            else:
                full = await client(GetFullChatRequest(chat.id))
                total_members = len(full.users)

                owner_entity = None
                admin_mentions = []

                for u in full.users:
                    entity = await client.get_entity(u.id)
                    mention = f"[{get_display_name(entity)}](tg://user?id={entity.id})"
                    if getattr(u, "creator", False) or getattr(u.admin_rights, "is_creator", False):
                        owner_entity = entity
                        owner_mention = mention
                    elif getattr(u, "admin_rights", None):
                        admin_mentions.append(mention)

                if owner_entity is None and admin_mentions:
                    owner_mention = admin_mentions[0]
                    admins = admin_mentions[1:]
                else:
                    admins = admin_mentions

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
            f"Admins ({len(admins)}):\n" + ("\n".join(admins) if admins else "None")
        )
        await event.reply(msg)
