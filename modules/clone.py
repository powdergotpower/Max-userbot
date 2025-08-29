import random
from telethon import events
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
import io

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.clone(?:\s+(.+))?$', outgoing=True))
    async def clone_profile(event):
        arg = event.pattern_match.group(1)
        if arg:
            target = arg.strip()
        elif event.is_reply:
            target = (await event.get_reply_message()).sender_id
        else:
            await event.reply("Usage:\n.clone @username\nor reply to a user's message with .clone")
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

        # Update first and last name
        first_name = full.user.first_name or ""
        last_name = full.user.last_name or ""
        await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))

        # Try to clone username with appended random digits if necessary
        base_username = full.user.username
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
            else:
                await event.reply("Failed to set username; all attempts taken or username unavailable.")
        else:
            await event.reply("The target user has no username to clone.")

        # Clone bio/about
        about = full.full_user.about or ""
        await client(UpdateProfileRequest(about=about))

        # Clone profile photo (first)
        photos = await client.get_profile_photos(target_entity)
        if photos.total > 0:
            photo = photos[0]
            bytes_io = io.BytesIO()
            await client.download_media(photo, bytes_io)
            bytes_io.seek(0)
            await client(DeletePhotosRequest(await client.get_profile_photos('me')))
            await client(UploadProfilePhotoRequest(await client.upload_file(bytes_io)))

        await event.reply(f"Cloned profile of [{target_entity.first_name}](tg://user?id={target_entity.id}) successfully.")
