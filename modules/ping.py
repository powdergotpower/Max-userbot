from telethon import events
import time

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.ping$'))
    async def ping_handler(event):
        chat = await event.get_chat()
        start_time = time.time()
        msg = await event.reply("🏓 Pong!")
        end_time = time.time()
        delta = int((end_time - start_time) * 1000)  # ms

        # Only show extra text in groups if needed
        if hasattr(chat, "id"):
            await msg.edit(f"Pong! 🏓\nResponse time: {delta}ms")
        else:
            await msg.edit(f"Pong! 🏓\nResponse time: {delta}ms\nThis command only works in groups.")
