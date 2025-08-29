# clone.py
import os
import html
from telethon import events, functions
from telethon.tl.functions.users import GetFullUserRequest
from Config import TEMP_DIR  # make sure TEMP_DIR exists

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.clone(?:\s+(.+))?$', outgoing=True))
    async def clone_profile(event):
        # Determine target
        arg = event.pattern_match.group(1)
        if arg:
            target = arg.strip()
        elif event.is_reply:
            msg = await event.get_reply_message()
            if not msg:
                await event.reply("Reply to a user's message or provide a username.")
                return
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
            user = getattr(full, 'user', target_entity)
        except Exception as e:
            await event.reply(f"Failed to get user info: {e}")
            return

        # Clone first and last name
        first_name = html.escape(user.first_name or "")
        last_name = html.escape(user.last_name or "")
        await client(functions.account.UpdateProfileRequest(first_name=first_name, last_name=last_name))

        # Clone bio/about safely
        about = getattr(getattr(full, "full_user", None), "about", "")
        if about:
            await client(functions.account.UpdateProfileRequest(about=about))

        # Clone profile photo
        photos = await client.get_profile_photos(target_entity)
        if photos.total > 0:
            # Ensure TEMP_DIR exists
            os.makedirs(TEMP_DIR, exist_ok=True)
            photo_path = await client.download_media(photos[0], file=os.path.join(TEMP_DIR, "temp.jpg"))

            # Delete current profile photos
            current_photos = await client.get_profile_photos("me")
            if current_photos.total > 0:
                await client(functions.photos.DeletePhotosRequest(current_photos))

            # Upload new photo
            await client(functions.photos.UploadProfilePhotoRequest(await client.upload_file(photo_path)))

        await event.reply(f"✅ Cloned profile of [{user.first_name}](tg://user?id={user.id}) successfully.")
