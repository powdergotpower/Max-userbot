from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_display_name

def register(client):

    @client.on(events.NewMessage(pattern=r'\.info(?: |$)(.*)'))
    async def info_handler(event):
        arg = event.pattern_match.group(1).strip()

        if event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
        elif arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Usage: .info @username or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or specify username/id like .info @username")
            return

        try:
            full = await client(GetFullUserRequest(user.id))
        except Exception as e:
            await event.reply(f"Failed to get full user info: {e}")
            return

        mutual_chats = len(await client.get_common_chats(user.id))
        about = full.full_user.about or "None"

        status = "Unknown"
        try:
            if user.status:
                if hasattr(user.status, "was_online") and user.status.was_online:
                    status = f"Last seen at {user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
                elif hasattr(user.status, "online") and user.status.online:
                    status = "Online now"
                else:
                    status = str(user.status)
        except Exception:
            pass

        first_name = user.first_name or "None"
        last_name = user.last_name or "None"
        username = user.username or "None"
        bot = user.bot

        restricted = "No"
        if hasattr(user, "restricted") and user.restricted:
            restricted = "Yes"

        msg = (
            f"**User Info:**\n"
            f"Name: {first_name} {last_name}\n"
            f"ID: `{user.id}`\n"
            f"Username: @{username}\n"
            f"Bot: {bot}\n"
            f"Last Seen: {status}\n"
            f"Mutual Groups: {mutual_chats}\n"
            f"Restricted: {restricted}\n"
            f"Bio/About: {about}"
        )

        await event.reply(msg)
