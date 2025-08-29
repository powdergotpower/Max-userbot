import html
import io
import random
from telethon import events
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest

from Config import Config  # Absolute import
from sql_helper.globals import gvarstatus
from utils import edit_delete, get_user_from_event  # Adjust according to your project

ALIVE_NAME = gvarstatus("FIRST_NAME") or "YourName"
BOTLOG = True
BOTLOG_CHATID = gvarstatus("BOTLOG_CHATID") or None
plugin_category = "utils"

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.clone(?:\s+(.+))?$', outgoing=True))
    async def clone_profile(event):
        replied_user, error_i_a = await get_user_from_event(event)
        if replied_user is None:
            await event.reply("Reply to a user or provide a username/user_id to clone.")
            return

        user_id = replied_user.id
        first_name = html.escape(replied_user.first_name) if replied_user.first_name else ""
        last_name = html.escape(replied_user.last_name) if replied_user.last_name else ""
        if not last_name:
            last_name = "⁪⁬⁮⁮⁮⁮ ‌‌‌‌"

        # Get full user for bio
        try:
            full = await client(GetFullUserRequest(user_id))
            user_bio = getattr(full, "about", "") or ""
        except Exception:
            user_bio = ""

        # Update name and bio
        await client(UpdateProfileRequest(first_name=first_name))
        await client(UpdateProfileRequest(last_name=last_name))
        if user_bio:
            await client(UpdateProfileRequest(about=user_bio))

        # Update username (optional)
        base_username = getattr(replied_user, "username", None)
        if base_username:
            tried_username = base_username
            for _ in range(5):
                try:
                    await client(UpdateUsernameRequest(tried_username))
                    break
                except Exception:
                    suffix = str(random.randint(10, 999))
                    tried_username = (base_username + suffix)[:32]

        # Clone profile photo
        try:
            photos = await client.get_profile_photos(user_id)
            if photos.total > 0:
                photo = photos[0]
                bytes_io = io.BytesIO()
                await client.download_media(photo, bytes_io)
                bytes_io.seek(0)
                await client(DeletePhotosRequest(await client.get_profile_photos('me')))
                pfile = await client.upload_file(bytes_io)
                await client(UploadProfilePhotoRequest(pfile))
        except Exception as e:
            await event.reply(f"Profile photo clone failed: {e}")

        await event.reply(f"✅ Cloned profile of [{first_name}](tg://user?id={user_id}) successfully.")

    # Revert command
    @client.on(events.NewMessage(pattern=r'^\.revert$', outgoing=True))
    async def revert_profile(event):
        firstname = gvarstatus("FIRST_NAME") or ALIVE_NAME
        lastname = gvarstatus("LAST_NAME") or ""
        bio = gvarstatus("DEFAULT_BIO") or "This is my default bio"
        # Delete current profile photo
        await client(functions.photos.DeletePhotosRequest(await client.get_profile_photos('me')))
        await client(UpdateProfileRequest(first_name=firstname))
        await client(UpdateProfileRequest(last_name=lastname))
        await client(UpdateProfileRequest(about=bio))
        await edit_delete(event, "✅ Successfully reverted profile.")
        if BOTLOG and BOTLOG_CHATID:
            await client.send_message(BOTLOG_CHATID, "#REVERT\nReverted profile successfully.")
