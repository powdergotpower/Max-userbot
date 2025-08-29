from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_display_name

def register(client):

    @client.on(events.NewMessage(pattern=r'\.info(?: |$)(.*)'))
    async def info_handler(event):
        arg = event.pattern_match.group(1).strip()
        user = None

        # 1️⃣ PM without argument → get the chat partner
        if event.is_private and not arg and not event.is_reply:
            user = await event.get_chat()
        # 2️⃣ Reply in group → get sender
        elif event.is_reply and not arg:
            user = await event.get_reply_message().get_sender()
        # 3️⃣ Username or ID provided
        elif arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use `.info @username` or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or use `.info @username` or `.info user_id`.")
            return

        # Fetch full user details
        try:
            full = await client(GetFullUserRequest(user.id))
        except Exception:
            full = None

        first_name = user.first_name or "N/A"
        last_name = user.last_name or ""
        username = user.username or "N/A"

        # Last seen / online
        status = "Unknown"
        if user.status:
            try:
                if getattr(user.status, "was_online", None):
                    status = f"Last seen at {user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
                elif getattr(user.status, "expires", None) is None:
                    status = "Online now"
                else:
                    status = f"{user.status.__class__.__name__}"
            except Exception:
                status = "Unknown"

        # Mutual groups
        try:
            mutual = await client.get_common_chats(user.id)
            mutual_count = len(mutual)
        except Exception:
            mutual_count = 0

        msg = (
            f"**User Info:**\n"
            f"Name: {first_name} {last_name}\n"
            f"ID: `{user.id}`\n"
            f"Username: @{username}\n"
            f"Last Seen: {status}\n"
            f"Mutual Groups with you: {mutual_count}"
        )

        await event.reply(msg)
