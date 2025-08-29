from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest

def register(client):

    async def make_username_available(username):
        """Try to find an available username by appending small letters if taken"""
        from string import ascii_lowercase

        try:
            # Try original username first
            await client(UpdateUsernameRequest(username))
            return username
        except:
            pass

        # Try username_a, username_b, ...
        for letter in ascii_lowercase:
            new_username = f"{username}_{letter}"
            try:
                await client(UpdateUsernameRequest(new_username))
                return new_username
            except:
                continue
        return None  # Couldn't find available

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

        # Clone first_name, last_name
        try:
            await client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or ""
            ))

            # Clone username if exists
            final_username = None
            if user.username:
                final_username = await make_username_available(user.username)

            msg = f"Cloned profile of {user.first_name or ''} {user.last_name or ''} successfully ✅"
            if final_username:
                msg += f"\nUsername set to @{final_username}"
            else:
                if user.username:
                    msg += "\nOriginal username unavailable, used only name."

            await event.reply(msg)

        except Exception as e:
            await event.reply(f"Failed to clone profile: {e}")
