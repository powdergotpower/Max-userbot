import random
import io
from telethon import events
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest

def register(client):

    @client.on(events.NewMessage(pattern=r'\.clone(?:\s+(.+))?'))
    async def clone_profile(event):
        arg = event.pattern_match.group(1)

        # Determine target
        if arg:
            target = arg.strip()
        elif event.is_reply:
            reply_msg = await event.get_reply_message()
            target = reply_msg.sender_id
        else:
            # PM or no argument
            target = event.sender_id  # clone self if in PM

        try:
            target_entity = await client.get_entity(target)
        except Exception as e:
            await event.reply(f"Failed to find user: {e}")
            return

        try:
            full = await client(GetFullUserRequest(target_entity.id))
        except Exception as e:
            await event.reply(f"Failed to get user info: {e}")
            return

        # user object
        user = getattr(full, 'user', None) or target_entity

        # Change first and last name
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))

        # Clone username with random suffix attempts
        base_username = getattr(user, 'username', None)
        if base_username:
            tried_username = base_username
            for _ in range(5):
                try:
                    await client(UpdateUsernameRequest(tried_username))
                    break
                except Exception:
                    suffix = str(random.randint(10, 999))
                    new_username = (base_username + suffix)[:32]
                    tried_username = new_username

        # Clone bio/about
        about = getattr(full, 'about', "") or ""
        await client(UpdateProfileRequest(about=about))

        # Clone profile photo
        photos = await client.get_profile_photos(target_entity)
        if photos.total > 0:
            photo = photos[0]
            bytes_io = io.BytesIO()
            await client.download_media(photo, bytes_io)
            bytes_io.seek(0)
            # Delete current photos
            await client(DeletePhotosRequest(await client.get_profile_photos('me')))
            # Upload new profile photo
            await client(UploadProfilePhotoRequest(await client.upload_file(bytes_io)))

        await event.reply(f"✅ Cloned profile of [{user.first_name}](tg://user?id={user.id}) successfully.")
