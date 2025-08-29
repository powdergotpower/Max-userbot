from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, PinMessageRequest, UnpinMessageRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import BadRequestError, UserIdInvalidError

from main import client  # Adjust if your main.py exposes the client
from helpers.utils import get_user_from_event, _format  # Make sure helpers exists
from core.data import _sudousers_list

BOTLOG = True
BOTLOG_CHATID = -100123456789  # Replace with your bot log chat id

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

# -----------------------------
# Kick command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.kick(?: |$)([\s\S]*)"))
async def kick(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return await event.reply("No user found to kick.")
    try:
        await client.kick_participant(event.chat_id, user.id)
        text = f"`Kicked` [{user.first_name}](tg://user?id={user.id})!"
        if reason:
            text += f"\nReason: {reason}"
        await event.reply(text)
    except BadRequestError as e:
        await event.reply(f"`Cannot kick user:` {e}")

# -----------------------------
# Ban command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.ban(?: |$)([\s\S]*)"))
async def ban(event):
    user, reason = await get_user_from_event(event)
    if not user:
        return await event.reply("No user found to ban.")
    try:
        await client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
        text = f"`Banned` [{user.first_name}](tg://user?id={user.id})!"
        if reason:
            text += f"\nReason: {reason}"
        await event.reply(text)
        if BOTLOG:
            await client.send_message(
                BOTLOG_CHATID,
                f"#BAN\nUSER: [{user.first_name}](tg://user?id={user.id})\nCHAT: {event.chat_id}\nREASON: {reason if reason else 'None'}"
            )
    except BadRequestError as e:
        await event.reply(f"`Cannot ban user:` {e}")

# -----------------------------
# Unban command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.unban(?: |$)([\s\S]*)"))
async def unban(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return await event.reply("No user found to unban.")
    try:
        await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await event.reply(f"`Unbanned` [{user.first_name}](tg://user?id={user.id}) successfully.")
    except UserIdInvalidError:
        await event.reply("`User not found or invalid ID`")
    except Exception as e:
        await event.reply(f"Error: {e}")

# -----------------------------
# Pin command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.pin(?: |$)"))
async def pin(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a message to pin it.")
    try:
        await client(PinMessageRequest(event.chat_id, reply.id, notify=True))
        await event.reply("Message pinned successfully!")
    except BadRequestError:
        await event.reply("I don't have permission to pin messages.")

# -----------------------------
# Unpin command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.unpin(?: |$)"))
async def unpin(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("Reply to a message to unpin it.")
    try:
        await client(UnpinMessageRequest(event.chat_id, reply.id))
        await event.reply("Message unpinned successfully!")
    except BadRequestError:
        await event.reply("I don't have permission to unpin messages.")

# -----------------------------
# Clean command
# -----------------------------
@client.on(events.NewMessage(pattern=r"\.clean (\d+)"))
async def clean(event):
    count = int(event.pattern_match.group(1))
    msgs = await client.get_messages(event.chat_id, limit=count)
    try:
        await client(DeleteHistoryRequest(event.chat_id, max_id=msgs[0].id))
        await event.reply(f"Deleted last {count} messages.")
    except BadRequestError:
        await event.reply("I don't have permission to delete messages.")
