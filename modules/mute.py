from telethon import events
from telethon.tl.types import User, Channel, Chat
from telethon.utils import get_display_name

# Dictionary to store muted users per chat
muted_users = {}

def register(client):

    # .mute command
    @client.on(events.NewMessage(pattern=r'\.mute(?: |$)(.*)'))
    async def mute_handler(event):
        chat = await event.get_chat()
        chat_id = event.chat_id
        arg = event.pattern_match.group(1).strip()

        if chat_id not in muted_users:
            muted_users[chat_id] = []

        # Determine the user to mute
        if arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use `.mute @username` or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        elif event.is_reply:
            reply = await event.get_reply_message()
            user = await reply.get_sender()
        else:
            await event.reply("Reply to a user or use `.mute @username` or `.mute user_id`.")
            return

        if user.id in muted_users[chat_id]:
            await event.reply(f"{get_display_name(user)} is already muted.")
            return

        muted_users[chat_id].append(user.id)

        # Custom messages
        if getattr(user, "bot", False):
            msg = f"{get_display_name(user)} is now muted 🤖"
        else:
            msg = f"Shhhh {get_display_name(user)}! Stay quiet 🔇"

        await event.reply(msg)

    # .unmute command
    @client.on(events.NewMessage(pattern=r'\.unmute(?: |$)(.*)'))
    async def unmute_handler(event):
        chat_id = event.chat_id
        arg = event.pattern_match.group(1).strip()

        if chat_id not in muted_users:
            muted_users[chat_id] = []

        if arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use `.unmute @username` or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        elif event.is_reply:
            reply = await event.get_reply_message()
            user = await reply.get_sender()
        else:
            await event.reply("Reply to a user or use `.unmute @username` or `.unmute user_id`.")
            return

        if user.id not in muted_users[chat_id]:
            await event.reply(f"{get_display_name(user)} is not muted.")
            return

        muted_users[chat_id].remove(user.id)
        await event.reply(f"{get_display_name(user)} is now unmuted ✅")

    # .muteall command (mute everyone except admins and owners)
    @client.on(events.NewMessage(pattern=r'\.muteall'))
    async def muteall_handler(event):
        chat = await event.get_chat()
        chat_id = event.chat_id

        if chat_id not in muted_users:
            muted_users[chat_id] = []

        async for user in client.iter_participants(chat):
            if user.bot:
                continue
            try:
                rights = getattr(user, "admin_rights", None)
                creator = getattr(user, "creator", False)
                if rights or creator:
                    continue
                if user.id not in muted_users[chat_id]:
                    muted_users[chat_id].append(user.id)
            except Exception:
                continue

        await event.reply("Everyone except admins and owner has been muted 🔇")

    # Delete messages of muted users automatically
    @client.on(events.NewMessage)
    async def delete_muted_messages(event):
        chat_id = event.chat_id
        sender = await event.get_sender()
        if chat_id in muted_users and sender.id in muted_users[chat_id]:
            await event.delete()
