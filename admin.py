# modules/admin.py
from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError

def register(client):

    @client.on(events.NewMessage(pattern=r"\.ban ?(.*)", outgoing=True))
    async def ban_user(event):
        if not event.is_group:
            return await event.respond("❌ This command only works in groups.")

        if not event.is_reply:
            return await event.respond("⚠️ Reply to a user to ban them.")

        try:
            user = await event.get_reply_message()
            reason = event.pattern_match.group(1) or "No reason"
            await client.edit_permissions(event.chat_id, user.sender_id, view_messages=False)
            await event.respond(f"🚫 Banned [{user.sender.first_name}](tg://user?id={user.sender_id})\nReason: `{reason}`")
        except ChatAdminRequiredError:
            await event.respond("❌ I need admin rights with ban permissions.")
        except UserAdminInvalidError:
            await event.respond("⚠️ Cannot ban another admin.")

    @client.on(events.NewMessage(pattern=r"\.kick ?(.*)", outgoing=True))
    async def kick_user(event):
        if not event.is_group:
            return await event.respond("❌ This command only works in groups.")

        if not event.is_reply:
            return await event.respond("⚠️ Reply to a user to kick them.")

        try:
            user = await event.get_reply_message()
            reason = event.pattern_match.group(1) or "No reason"
            await client.kick_participant(event.chat_id, user.sender_id)
            await event.respond(f"👢 Kicked [{user.sender.first_name}](tg://user?id={user.sender_id})\nReason: `{reason}`")
        except ChatAdminRequiredError:
            await event.respond("❌ I need admin rights with kick permissions.")
        except UserAdminInvalidError:
            await event.respond("⚠️ Cannot kick another admin.")

    @client.on(events.NewMessage(pattern=r"\.mute ?(.*)", outgoing=True))
    async def mute_user(event):
        if not event.is_group:
            return await event.respond("❌ This command only works in groups.")

        if not event.is_reply:
            return await event.respond("⚠️ Reply to a user to mute them.")

        try:
            user = await event.get_reply_message()
            reason = event.pattern_match.group(1) or "No reason"
            await client.edit_permissions(event.chat_id, user.sender_id, send_messages=False)
            await event.respond(f"🔇 Muted [{user.sender.first_name}](tg://user?id={user.sender_id})\nReason: `{reason}`")
        except ChatAdminRequiredError:
            await event.respond("❌ I need admin rights with mute permissions.")
        except UserAdminInvalidError:
            await event.respond("⚠️ Cannot mute another admin.")

    @client.on(events.NewMessage(pattern=r"\.unmute", outgoing=True))
    async def unmute_user(event):
        if not event.is_group:
            return await event.respond("❌ This command only works in groups.")

        if not event.is_reply:
            return await event.respond("⚠️ Reply to a user to unmute them.")

        try:
            user = await event.get_reply_message()
            await client.edit_permissions(event.chat_id, user.sender_id, send_messages=True)
            await event.respond(f"🔊 Unmuted [{user.sender.first_name}](tg://user?id={user.sender_id})")
        except ChatAdminRequiredError:
            await event.respond("❌ I need admin rights with mute permissions.")
