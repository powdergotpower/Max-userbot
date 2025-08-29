import random
from telethon import events
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest, UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto
import io

def register(client):

    @client.on(events.NewMessage(pattern=r'\.clone(?: |$)(.*)'))
    async def clone_profile(event):
        if event.pattern_match.group(1):
            target = event.pattern_match.group(1).strip()
        elif event.is_reply:
            target = (await event.get_reply_message()).sender_id
        else:
            await event.reply("Usage: .clone @username or reply to a user's message")
            return

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

        # Change first and last name
        first_name = full.user.first_name or ""
        last_name = full.user.last_name or ""
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))

        # Attempt to clone username with fallback random suffix if taken
        base_username = full.user.username
        if base_username:
            tried_username = base_username
            success = False
            for _ in range(5):  # try up to 5 times with random suffix
                try:
                    await client(UpdateUsernameRequest(tried_username))
                    success = True
                    break
                except Exception:
                    # Append a random 2 or 3 digit number to username
                    suffix = str(random.randint(10, 999))
                    # Usernames must be 5 to 32 chars
                    new_username = (base_username + suffix)[:32]
                    tried_username = new_username
            if not success:
                await event.reply("Failed to clone username, all attempts taken.")
        else:
            await event.reply("Target user has no username to clone.")

        # Change bio/about
        about = full.full_user.about or ""
        await client(UpdateProfileRequest(about=about))

        # Clone profile photo - first photo only
        photos = await client.get_profile_photos(target_entity)
        if photos.total > 0:
            photo = photos[0]
            bytes_io = io.BytesIO()
            await client.download_media(photo, bytes_io)
            bytes_io.seek(0)
            # Delete all current profile photos
            await client(DeletePhotosRequest(await client.get_profile_photos('me')))
            # Upload new profile photo
            await client(UploadProfilePhotoRequest(await client.upload_file(bytes_io)))

        await event.reply(f"📝 Cloned profile of [{target_entity.first_name}](tg://user?id={target_entity.id}) successfully.")
