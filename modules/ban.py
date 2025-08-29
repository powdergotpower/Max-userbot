from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

def register(client):

    # .ban command
    @client.on(events.NewMessage(pattern=r'\.ban(?: |$)(.*)'))
    async def ban_handler(event):
        if not event.is_group:
            await event.reply("This command only works in groups.")
            return

        # Get the user to ban
        arg = event.pattern_match.group(1).strip()
        user = None
        if event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
        elif arg:
            try:
                user = await client.get_entity(arg)
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or provide @username/user_id to ban.")
            return

        rights = ChatBannedRights(
            until_date=None,
            view_messages=True,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_polls=True,
            change_info=True,
            invite_users=True,
            pin_messages=True
        )

        try:
            await client(EditBannedRequest(
                channel=event.chat_id,
                participant=user,
                banned_rights=rights
            ))
            await event.reply(f"🚫 {user.first_name} has been banned from this group.")
        except Exception as e:
            await event.reply(f"Failed to ban user: {e}")
