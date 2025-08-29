from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

muted_users = {}  # {chat_id: [user_id, ...]}

def register(client):

    # .mute command
    @client.on(events.NewMessage(pattern=r'\.mute(?: |$)(.*)'))
    async def mute_handler(event):
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
            await event.reply("Reply to a user or use .mute @username or .mute user_id.")
            return

        chat_id = event.chat_id
        muted_users.setdefault(chat_id, [])

        try:
            # Check if user is admin or owner
            participant = await client.get_permissions(chat, user)
            if participant.is_admin or participant.is_creator:
                # Cannot mute, delete messages instead
                muted_users[chat_id].append(user.id)
                await event.reply(f"Shhhh [{user.first_name}](tg://user?id={user.id}) stay quiet 😉")
            else:
                # Mute normal user
                rights = ChatBannedRights(
                    until_date=None,
                    send_messages=True
                )
                await client(EditBannedRequest(chat.id, user.id, rights))
                muted_users[chat_id].append(user.id)
                await event.reply(f"[{user.first_name}](tg://user?id={user.id}) has been muted ✅")
        except Exception as e:
            await event.reply(f"Failed to mute: {e}")

    # Optional: Delete messages of muted admins/owner
    @client.on(events.NewMessage)
    async def delete_muted_messages(event):
        chat_id = event.chat_id
        if chat_id in muted_users and event.sender_id in muted_users[chat_id]:
            try:
                await event.delete()
            except Exception:
                pass
