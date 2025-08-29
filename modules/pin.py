# modules/pin.py
from telethon import events
from telethon.tl.functions.messages import UpdatePinnedMessageRequest, UnpinAllMessagesRequest

def register(client):

    # .pin - Pin a message
    @client.on(events.NewMessage(pattern=r'\.pin'))
    async def pin_handler(event):
        if not event.is_group:
            await event.reply("This command only works in groups.")
            return

        if not event.is_reply:
            await event.reply("Reply to a message to pin it.")
            return

        try:
            msg = await event.get_reply_message()
            await client(UpdatePinnedMessageRequest(event.chat_id, id=msg.id, silent=True))
            await event.reply("✅ Message pinned successfully!")
        except Exception as e:
            await event.reply(f"Failed to pin message: {e}")

    # .unpin - Unpin all pinned messages
    @client.on(events.NewMessage(pattern=r'\.unpin'))
    async def unpin_handler(event):
        if not event.is_group:
            await event.reply("This command only works in groups.")
            return

        try:
            await client(UnpinAllMessagesRequest(event.chat_id))
            await event.reply("✅ All messages unpinned successfully!")
        except Exception as e:
            await event.reply(f"Failed to unpin messages: {e}")
