from telethon import events
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

# Track muted users per chat
muted_users = {}  # {chat_id: set(user_ids)}
mute_active = {}  # {chat_id: True/False} to control admin/owner deletion

def register(client):

    # Mute command
    @client.on(events.NewMessage(pattern=r'\.mute(?: |$)(.*)'))
    async def mute_handler(event):
        chat = await event.get_chat()
        chat_id = event.chat_id

        if not isinstance(chat, (Channel, Chat)):
            await event.reply("This command only works in groups.")
            return

        if chat_id not in muted_users:
            muted_users[chat_id] = set()
        mute_active[chat_id] = True  # Activate deleting admin/owner messages

        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await (await event.get_reply_message()).get_sender()
        elif arg:
            try:
                if arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    user = await client.get_entity(int(arg))
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or use .mute @username or .mute user_id.")
            return

        muted_users[chat_id].add(user.id)
        await event.reply(f"{get_display_name(user)} is now muted ✅")

    # Unmute command
    @client.on(events.NewMessage(pattern=r'\.unmute(?: |$)(.*)'))
    async def unmute_handler(event):
        chat_id = event.chat_id
        if chat_id not in muted_users:
            muted_users[chat_id] = set()
        mute_active[chat_id] = False  # Stop deleting admin/owner messages

        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await (await event.get_reply_message()).get_sender()
        elif arg:
            try:
                if arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    user = await client.get_entity(int(arg))
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or use .unmute @username or .unmute user_id.")
            return

        if user.id in muted_users[chat_id]:
            muted_users[chat_id].remove(user.id)
            await event.reply(f"{get_display_name(user)} is now unmuted ✅")
        else:
            await event.reply(f"{get_display_name(user)} was not muted.")

    # Delete messages of muted users
    @client.on(events.NewMessage)
    async def auto_delete_muted(event):
        chat_id = event.chat_id
        if chat_id not in muted_users:
            return

        sender = await event.get_sender()
        if not sender:
            return

        sender_id = sender.id

        # Always delete if user is muted
        if sender_id in muted_users[chat_id]:
            await event.delete()
        # Delete admins/owner messages if mute is active
        elif mute_active.get(chat_id):
            rights = getattr(sender, "admin_rights", None)
            is_owner = getattr(sender, "creator", False)
            if rights or is_owner:
                await event.delete()
