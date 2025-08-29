from telethon import events
from telethon.tl.functions.messages import DeleteMessagesRequest

def register(client):
    muted_users = {}  # chat_id: set of muted user IDs

    # -----------------------------
    # .mute command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.mute(?: |$)(.*)'))
    async def mute_handler(event):
        chat = await event.get_chat()
        chat_id = event.chat_id

        if not hasattr(muted_users, chat_id):
            muted_users[chat_id] = set()
        muted_set = muted_users.setdefault(chat_id, set())

        # Get target user
        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
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
            await event.reply("Reply to a user or use .mute @username or .mute user_id")
            return

        # Check if target is admin/owner
        admin = False
        creator = False
        try:
            participant = await client.get_permissions(chat, user)
            admin = participant.is_admin
            creator = participant.is_creator
        except Exception:
            pass  # user not in chat or private chat

        # Add to muted set
        muted_set.add(user.id)

        # Reply according to role
        if creator:
            await event.reply(f"Sometimes {user.first_name} should stay quiet 😉")
        elif admin:
            await event.reply(f"Have some rest, {user.first_name} admin 😎")
        else:
            await event.reply(f"Shhhh @{user.username or user.first_name}, stay muted 🤫")

    # -----------------------------
    # .unmute command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.unmute(?: |$)(.*)'))
    async def unmute_handler(event):
        chat_id = event.chat_id
        muted_set = muted_users.setdefault(chat_id, set())

        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
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
            await event.reply("Reply to a user or use .unmute @username or .unmute user_id")
            return

        muted_set.discard(user.id)
        await event.reply(f"User {user.first_name} is now unmuted ✅")

    # -----------------------------
    # Delete messages from muted users
    # -----------------------------
    @client.on(events.NewMessage)
    async def auto_delete(event):
        chat_id = event.chat_id
        muted_set = muted_users.get(chat_id, set())

        if event.sender_id in muted_set:
            try:
                await client(DeleteMessagesRequest([event.message.id]))
            except Exception:
                pass
