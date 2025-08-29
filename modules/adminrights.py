from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.adminright$', outgoing=True))
    async def admin_rights_handler(event):
        if not event.is_group and not event.is_channel:
            await event.reply("This command only works in groups or channels.")
            return

        reply_msg = await event.get_reply_message()
        if not reply_msg:
            await event.reply("Reply to an admin's message to check their admin rights.")
            return

        user_id = reply_msg.sender_id
        chat_id = event.chat_id

        try:
            participant = await client(GetParticipantRequest(chat_id, user_id))
            participant_obj = participant.participant
        except Exception as e:
            await event.reply(f"Failed to get participant info: {e}")
            return

        if isinstance(participant_obj, ChannelParticipantCreator):
            await event.reply("User is the owner (creator) of this chat.")
            return

        if isinstance(participant_obj, ChannelParticipantAdmin):
            rights = participant_obj.admin_rights

            rights_list = []
            if rights.change_info:
                rights_list.append("Change Info")
            if rights.post_messages:
                rights_list.append("Post Messages")
            if rights.edit_messages:
                rights_list.append("Edit Messages")
            if rights.delete_messages:
                rights_list.append("Delete Messages")
            if rights.ban_users:
                rights_list.append("Ban Users")
            if rights.invite_users:
                rights_list.append("Invite Users")
            if rights.pin_messages:
                rights_list.append("Pin Messages")
            if rights.add_admins:
                rights_list.append("Add Admins")
            if rights.manage_call:
                rights_list.append("Manage Voice Chats")
            if rights.anonymous:
                rights_list.append("Anonymous Admin")

            rights_str = ", ".join(rights_list) if rights_list else "No admin rights."

            await event.reply(f"Admin rights of user:\n{rights_str}")
        else:
            await event.reply("User is not an admin in this chat.")
