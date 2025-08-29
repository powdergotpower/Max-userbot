from telethon import events
import time

def register(client):

    @client.on(events.NewMessage(pattern=r'^\.p$'))
    async def p_handler(event):
        start = time.time()
        msg = await event.reply("Pong! 🏓")
        end = time.time()
        response_time = int((end - start) * 1000)
        await msg.edit(f"Pong! 🏓\nResponse time: {response_time}ms")
