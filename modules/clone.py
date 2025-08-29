# clone.py
import html
import io
import random
from telethon import events
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest
from Config import TEMP_DIR

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.clone(?:\s+(.+))?$', outgoing=True))
    async def clone_profile(event):
        # Determine target
        arg = event.pattern_match.group(1)
        if arg:
            target = arg.strip()
        elif event.is_reply:
            msg = await event.get_reply_message()
            target = msg.sender_id
        else:
            await event.reply("Usage:\n.clone @username\nor reply to a user's message with .clone")
            return

        # Fetch user entity
        try:
            target_entity = await client.get_entity(target)
        except Exception as e:
            await event.reply(f"Failed to find user: {e}")
            return

        # Fetch full user info
        try:
            full = await client(GetFullUserRequest(target_entity.id))
        except Exception as e:
            await event.reply(f"Failed to get user info: {e}")
            return

        user = getattr(full, 'user', target_entity)

        # Clone first and last name
        first_name = html.escape(user.first_name or "")
        last_name = html.escape(user.last_name or "")
        await client(functions.account.UpdateProfileRequest(first_name=first_name, last_name=last_name))

        # Clone username if exists
        base_username = getattr(user, "username", None)
        if base_username:
            tried_username = base_username
            for _ in range(5):
                try:
                    await client(functions.account.UpdateUsernameRequest(tried_username))
                    break
                except Exception:
                    suffix = str(random.randint(10, 999))
                    tried_username = (base_username + suffix)[:32]

        # Clone bio/about
        user_bio = getattr(full, "about", "")
        if user_bio:
            await client(functions.account.UpdateProfileRequest(about=user_bio))

        # Clone profile photo
        photos = await client.get_profile_photos(target_entity)
        if photos.total > 0:
            photo = photos[0]
            bytes_io = io.BytesIO()
            await client.download_media(photo, bytes_io)
            bytes_io.seek(0)
            # Delete current profile photos
            current_photos = await client.get_profile_photos("me")
            if current_photos.total > 0:
                await client(functions.photos.DeletePhotosRequest(current_photos))
            # Upload new profile photo
            await client(functions.photos.UploadProfilePhotoRequest(await client.upload_file(bytes_io)))

        await event.reply(f"✅ Cloned profile of [{user.first_name}](tg://user?id={user.id}) successfully.")
