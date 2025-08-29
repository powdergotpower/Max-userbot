from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

def register(client):
    
    @client.on(events.NewMessage(pattern=r'^\.kick(?: |$)(.*)'))
    async def kick_handler(event):
        chat = await event.get_chat()
        
        # Only work in groups or channels
        if not hasattr(chat, 'id'):
            await event.reply("This command only works in groups.")
            return
        
        reply = await event.get_reply_message()
        arg = event.pattern_match.group(1).strip()
        
        if reply:
            user_to_kick = await reply.get_sender()
        elif arg:
            try:
                if arg.isdigit():
                    user_to_kick = await client.get_entity(int(arg))
                elif arg.startswith('@'):
                    user_to_kick = await client.get_entity(arg)
                else:
                    await event.reply("Invalid input. Use .kick @username or reply to a user.")
                    return
            except Exception:
                await event.reply("User not found.")
                return
        else:
            await event.reply("Reply to a user or provide a username/user ID to kick.")
            return
        
        # Ban (kick) user temporarily
        banned_rights = ChatBannedRights(
            until_date=None,
            view_messages=True
        )
        
        try:
            await client(EditBannedRequest(chat.id, user_to_kick.id, banned_rights))
            await event.reply(f"{user_to_kick.first_name} has been kicked from this group ✅")
        except Exception as e:
            await event.reply(f"Failed to kick user: {e}")
