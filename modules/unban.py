from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

def register(client):

    # .unban command
    @client.on(events.NewMessage(pattern=r'\.unban(?: |$)(.*)'))
    async def unban_handler(event):
        if not event.is_group:
            await event.reply("This command only works in groups.")
            return

        # Get the user to unban
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
            await event.reply("Reply to a user or provide @username/user_id to unban.")
            return

        rights = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_polls=False,
            change_info=False,
            invite_users=False,
            pin_messages=False
        )

        try:
            await client(EditBannedRequest(
                channel=event.chat_id,
                participant=user,
                banned_rights=rights
            ))
            await event.reply(f"✅ {user.first_name} has been unbanned from this group.")
        except Exception as e:
            await event.reply(f"Failed to unban user: {e}")
