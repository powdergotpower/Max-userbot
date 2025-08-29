from telethon import events, types
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

# Store muted users in memory (or you can persist in a file/db)
MUTED_USERS = set()

async def get_participant(client, chat_id, user_id):
    try:
        return await client(GetParticipantRequest(chat_id, user_id))
    except:
        return None

def is_admin_or_owner(participant):
    if isinstance(participant.participant, ChannelParticipantAdmin):
        return "admin"
    elif isinstance(participant.participant, ChannelParticipantCreator):
        return "owner"
    return "member"

@client.on(events.NewMessage(pattern=r'\.mute(?: |$)(.*)'))
async def mute_handler(event):
    chat = await event.get_chat()
    if not getattr(chat, 'megagroup', False):
        await event.reply("This command works only in groups.")
        return

    # Get target user
    if event.is_reply:
        target = await event.get_reply_message()
        user = target.sender
    else:
        args = event.pattern_match.group(1)
        if not args:
            await event.reply("Reply or mention a user to mute.")
            return
        user = await event.client.get_entity(args)

    participant = await get_participant(event.client, event.chat_id, user.id)
    role = is_admin_or_owner(participant) if participant else "member"

    if role == "member":
        MUTED_USERS.add(user.id)
        await event.reply(f"Shhhh [{user.first_name}](tg://user?id={user.id}) stay quiet 😴")
    elif role == "admin":
        await event.reply(f"Have some rest, [{user.first_name}](tg://user?id={user.id}) 😎")
    elif role == "owner":
        await event.reply(f"Sometimes [{user.first_name}](tg://user?id={user.id}) should stay quiet 😉")

@client.on(events.NewMessage)
async def delete_muted_messages(event):
    if event.chat_id and event.sender_id in MUTED_USERS:
        try:
            await event.delete()
        except:
            pass
