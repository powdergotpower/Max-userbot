from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat, ChannelParticipantsAdmins
from telethon.utils import get_display_name

daily_messages = {}

def register(client):

    # Count messages daily for active user tracking
    @client.on(events.NewMessage)
    async def daily_counter(event):
        chat_id = event.chat_id
        daily_messages[chat_id] = daily_messages.get(chat_id, 0) + 1

    # .gcinfo to get group info
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
        admin_mentions = []

        try:
            # Supergroup / Channel
            if isinstance(chat, Channel):
                full = await client(GetFullChannelRequest(chat.id))
                total_members = full.full_chat.participants_count

                participants = await client(GetParticipantsRequest(
                    channel=chat,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=200,
                    hash=0
                ))

                owner_entity = None
                other_admins = []

                for p in participants.users:
                    entity = await client.get_entity(p.id)
                    mention = f"[{get_display_name(entity)}](tg://user?id={entity.id})"
                    if getattr(p, 'creator', False):
                        owner_entity = entity
                    else:
                        other_admins.append((entity, mention))

                if owner_entity:
                    owner_mention = f"[{get_display_name(owner_entity)}](tg://user?id={owner_entity.id})"
                elif other_admins:
                    # fallback: first admin as owner
                    owner_entity = other_admins[0][0]
                    owner_mention = other_admins[0][1]
                    other_admins = other_admins[1:]

                admin_mentions = [m[1] for m in other_admins]

            # Basic group
            else:
                full = await client(GetFullChatRequest(chat.id))
                total_members = len(full.users)

                owner_entity = None

                for u in full.users:
                    entity = await client.get_entity(u.id)
                    mention = f"[{get_display_name(entity)}](tg://user?id={entity.id})"
                    if getattr(u, "creator", False) or getattr(u.admin_rights, "is_creator", False):
                        owner_entity = entity
                        owner_mention = mention
                    elif getattr(u, "admin_rights", None):
                        admin_mentions.append(mention)

                if not owner_entity and admin_mentions:
                    # fallback: first admin as owner
                    owner_mention = admin_mentions[0]
                    admin_mentions = admin_mentions[1:]

        except Exception as e:
            await event.reply(f"Failed to fetch group info: {e}")
            return

        # Build admins list nicely
        admins_str = "\n".join(admin_mentions) if admin_mentions else "None"

        msg = (
            f"**Group Info:**\n"
            f"Title: {chat_title}\n"
            f"ID: `{chat_id}`\n"
            f"Total Members: {total_members}\n"
            f"Active Messages Today: {active_today}\n"
            f"Owner: {owner_mention}\n"
            f"Admins ({len(admin_mentions)}):\n{admins_str}"
        )

        await event.reply(msg)
