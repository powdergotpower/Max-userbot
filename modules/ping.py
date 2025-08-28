from telethon import events
import time

def register(client):
    @client.on(events.NewMessage(pattern=r'\.ping'))
    async def ping_handler(event):
        start = time.time()
        await event.edit("Pinging...")  # Edit your own message
        end = time.time()
        ms = int((end - start) * 1000)
        await event.edit(f"Pong! 🏓\nResponse time: {ms}ms")
