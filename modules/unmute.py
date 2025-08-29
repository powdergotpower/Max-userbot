from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

muted_users = {}  # This should be shared with mute.py if possible

def register(client):

    # .unmute command
    @client.on(events.NewMessage(pattern=r'\.unmute(?: |$)(.*)'))
    async def unmute_handler(event):
        chat = await event.get_chat()
        if event.is_private:
            await event.reply("This command only works in groups.")
            return

        arg = event.pattern_match.group(1).strip()
        if event.is_reply and not arg:
            user = await (await event.get_reply_message()).get_sender()
        elif arg:
            try:
                user = await client.get_entity(arg)
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or use .unmute @username or .unmute user_id.")
            return

        chat_id = event.chat_id
        muted_users.setdefault(chat_id, [])

        try:
            # Unmute by removing send message restrictions
            rights = ChatBannedRights(
                until_date=None,
                send_messages=False  # False to remove restriction
            )
            await client(EditBannedRequest(chat.id, user.id, rights))

            if user.id in muted_users[chat_id]:
                muted_users[chat_id].remove(user.id)

            await event.reply(f"[{user.first_name}](tg://user?id={user.id}) is now unmuted ✅")
        except Exception as e:
            await event.reply(f"Failed to unmute: {e}")
