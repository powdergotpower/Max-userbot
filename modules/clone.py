from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhoto
from telethon.tl.types import InputPhoto
import io

def register(client):

    @client.on(events.NewMessage(pattern=r'\.clone(?: |$)(.*)'))
    async def clone_handler(event):
        arg = event.pattern_match.group(1).strip()

        # Determine target user
        if event.is_private and not arg:
            await event.reply("Please reply to a user or provide a username/user_id to clone.")
            return
        try:
            if event.is_reply and not arg:
                user = await event.get_reply_message().sender
            elif arg:
                if arg.isdigit():
                    user = await client.get_entity(int(arg))
                elif arg.startswith("@"):
                    user = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use .clone @username or reply to a user.")
                    return
            else:
                user = await client.get_me()
        except Exception:
            await event.reply("Cannot find the user.")
            return

        msg = ""

        # Clone name
        try:
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
            msg += f"✅ Name cloned: {first_name} {last_name}\n"
        except Exception as e:
            msg += f"❌ Failed to clone name: {e}\n"

        # Clone profile photo
        try:
            photos = await client.get_profile_photos(user.id, limit=1)
            if photos.total > 0:
                photo_bytes = await client.download_media(photos[0], file=bytes)
                await client(UploadProfilePhoto(file=photo_bytes))
                msg += "✅ Profile photo cloned."
            else:
                msg += "⚠️ User has no profile photo."
        except Exception as e:
            msg += f"❌ Failed to clone profile photo: {e}"

        await event.reply(msg)
