from telethon import events
import os

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.view$', outgoing=True))
    async def view_handler(event):
        if not event.reply_to_msg_id:
            await event.edit("Reply to a view-once photo/video with `.view`")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("No view-once media found in the replied message.")
            return

        try:
            # Make a download folder
            if not os.path.exists("downloads"):
                os.makedirs("downloads")

            path = await client.download_media(reply.media, "downloads/")
            await event.edit(f"✅ Media saved: `{path}`")

        except Exception as e:
            await event.edit(f"❌ Failed: {str(e)}")
