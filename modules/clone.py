from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest

def register(client):

    @client.on(events.NewMessage(pattern=r'\.clone(?: |$)(.*)'))
    async def clone_handler(event):
        arg = event.pattern_match.group(1).strip()
        user = None

        # Reply first
        if event.is_reply and not arg:
            reply = await event.get_reply_message()
            user = await reply.get_sender()

        # Username or user_id
        elif arg:
            try:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use .clone @username or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return

        # PM: if no arg and not reply, clone chat partner
        elif event.is_private:
            user = await event.get_chat()

        else:
            await event.reply("Reply to a user or provide username/user_id to clone.")
            return

        # Now clone the profile
        try:
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            username = user.username or None

            await client(UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
                username=username
            ))

            await event.reply(f"Cloned profile of {first_name} {last_name} successfully ✅")

        except Exception as e:
            await event.reply(f"Failed to clone profile: {e}")
