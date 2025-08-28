from telethon import events
from datetime import datetime

AFK_ON = False
AFK_REASON = None
AFK_START = None
AFK_USERS_REPLIED = set()

def register(client):

    # Set AFK
    @client.on(events.NewMessage(pattern=r'\.afk', outgoing=True))
    async def set_afk(event):
        global AFK_ON, AFK_REASON, AFK_START, AFK_USERS_REPLIED
        AFK_REASON = event.raw_text.split(maxsplit=1)[1] if len(event.raw_text.split()) > 1 else "AFK"
        AFK_ON = True
        AFK_START = datetime.now()
        AFK_USERS_REPLIED.clear()
        await event.respond(f"✅ I am now AFK: {AFK_REASON}")

    # Remove AFK on any outgoing message
    @client.on(events.NewMessage(outgoing=True))
    async def remove_afk(event):
        global AFK_ON, AFK_REASON, AFK_START, AFK_USERS_REPLIED
        if AFK_ON:
            AFK_ON = False
            duration = int((datetime.now() - AFK_START).total_seconds())
            AFK_START = None
            AFK_USERS_REPLIED.clear()
            await event.respond(f"✅ I am back online! AFK duration: {duration}s")

    # Reply to PMs
    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        global AFK_ON, AFK_REASON, AFK_START, AFK_USERS_REPLIED

        if not AFK_ON:
            return

        # Ensure it's a PM
        if not event.is_private:
            return

        sender = await event.get_sender()
        if not sender or sender.bot:
            return

        user_id = sender.id

        if user_id in AFK_USERS_REPLIED:
            return

        AFK_USERS_REPLIED.add(user_id)
        duration = int((datetime.now() - AFK_START).total_seconds())

        # Use try/except to catch any Telethon quirks
        try:
            await event.reply(f"⏳ I am currently AFK ({AFK_REASON})\nAway for {duration}s")
        except Exception:
            pass
