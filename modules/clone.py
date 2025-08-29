import random
import string
from telethon import events
from telethon.tl.functions.photos import GetUserPhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.account import UpdateProfileRequest

def register(client):

    @client.on(events.NewMessage(pattern=r'\.clone(?: |$)(.*)'))
    async def clone_handler(event):
        arg = event.pattern_match.group(1).strip()
        if event.is_private and not arg:
            await event.reply("Reply to a user or provide username/user_id to clone.")
            return

        try:
            if event.is_reply and not arg:
                user = await (await event.get_reply_message()).sender
            elif arg:
                user = await client.get_entity(arg)
            else:
                await event.reply("Reply to a user or provide username/user_id to clone.")
                return
        except Exception:
            await event.reply("Could not find the user.")
            return

        first_name = getattr(user, "first_name", "")
        last_name = getattr(user, "last_name", "")
        username = getattr(user, "username", None)

        # Attempt to clone profile
        new_username = username
        if username:
            for _ in range(10):  # try up to 10 variations
                try:
                    await client(UpdateProfileRequest(
                        first_name=first_name,
                        last_name=last_name,
                        username=new_username
                    ))
                    break
                except Exception:
                    # Append random lowercase letter or digit
                    new_username = username + random.choice(string.ascii_lowercase + string.digits)
            else:
                new_username = None  # fallback if username couldn't be set

        else:
            # No username, just update name
            await client(UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name
            ))

        # Clone profile picture
        try:
            photos = await client(GetUserPhotosRequest(user.id, limit=1))
            if photos.photos:
                photo = photos.photos[0]
                await client(UploadProfilePhotoRequest(file=photo))
        except Exception:
            pass

        msg = f"Successfully cloned: {first_name} {last_name}"
        if new_username:
            msg += f" (@{new_username})"
        await event.reply(msg)
