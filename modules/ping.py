from telethon import events
from telethon.tl.functions.messages import UpdatePinnedMessageRequest

def register(client):

    # Only trigger on exact .pin command
    @client.on(events.NewMessage(pattern=r'^\.pin$'))
    async def pin_handler(event):
        if not event.is_group:
            await event.reply("This command is for groups only.")
            return
        if not event.is_reply:
            await event.reply("Reply to a message to pin it.")
            return
        msg = await event.get_reply_message()
        await client(UpdatePinnedMessageRequest(peer=event.chat_id, id=msg.id, silent=True))
        await event.reply("Message pinned ✅")
