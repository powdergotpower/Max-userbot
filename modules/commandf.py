from telethon import events

AUTHORIZED_USERS = {8032922682}  # Your user ID(s)

def register(client):

    @client.on(events.NewMessage(pattern=r'^\..+', incoming=True), priority=-10)
    async def command_filter(event):
        if event.sender_id not in AUTHORIZED_USERS:
            # Stop event propagation, so other handlers won't run
            await event.cancel()
