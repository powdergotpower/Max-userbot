import html
import io
from telethon import events
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest

from ..Config import Config
from ..sql_helper.globals import gvarstatus
from . import edit_delete, catub, BOTLOG, BOTLOG_CHATID, ALIVE_NAME

plugin_category = "utils"

@catub.cat_cmd(
    pattern=r"clone(?:\s|$)([\s\S]*)",
    command=("clone", plugin_category),
    info={
        "header": "Clone the account of the mentioned or replied user",
        "usage": "{tr}clone <username/userid/reply>",
    },
)
async def clone_profile(event):
    replied_user, error_i_a = await catub.get_user_from_event(event)
    if replied_user is None:
        await event.reply(error_i_a or "Failed to fetch user.")
        return

    user_id = replied_user.id
    profile_pic = await event.client.download_profile_photo(user_id, Config.TEMP_DIR)

    # Prepare first and last names
    first_name = html.escape(replied_user.first_name or "")
    last_name = html.escape(replied_user.last_name or "")
    if not last_name:
        last_name = "⁪⁬⁮⁮⁮⁮ ‌‌‌‌"

    # Get full user info for bio
    full_user = (await event.client(GetFullUserRequest(user_id))).full_user
    user_bio = getattr(full_user, "about", "")

    # Update profile
    await event.client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
    if user_bio:
        await event.client(UpdateProfileRequest(about=user_bio))

    # Update profile photo
    if profile_pic:
        pfile = await event.client.upload_file(profile_pic)
        # Delete current photos
        current_photos = await event.client.get_profile_photos("me")
        if current_photos.total > 0:
            await event.client(DeletePhotosRequest(current_photos))
        await event.client(UploadProfilePhotoRequest(pfile))

    await edit_delete(event, f"✅ Successfully cloned [{first_name}](tg://user?id={user_id})")
    
    # Log if enabled
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#CLONED\nSuccessfully cloned [{first_name}](tg://user?id={user_id})",
        )

@catub.cat_cmd(
    pattern=r"revert$",
    command=("revert", plugin_category),
    info={
        "header": "Revert back to your original profile",
        "note": "Requires DEFAULT_USER set in DB",
        "usage": "{tr}revert",
    },
)
async def revert_profile(event):
    # Fetch saved default values
    firstname = gvarstatus("FIRST_NAME") or ALIVE_NAME
    lastname = gvarstatus("LAST_NAME") or ""
    bio = gvarstatus("DEFAULT_BIO") or "This is my default bio."

    # Delete current profile photo
    current_photos = await event.client.get_profile_photos("me", limit=1)
    if current_photos.total > 0:
        await event.client(DeletePhotosRequest(current_photos))

    # Revert profile
    await event.client(UpdateProfileRequest(first_name=firstname, last_name=lastname, about=bio))
    await edit_delete(event, "✅ Successfully reverted to your original profile")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#REVERT\nSuccessfully reverted profile back to original",
    )
