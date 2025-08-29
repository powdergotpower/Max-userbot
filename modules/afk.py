from telethon import events
from datetime import datetime

AFK_ON = False
AFK_REASON = ""
AFK_START = None

def register(client):

    @client.on(events.NewMessage(pattern=r'\.afk', outgoing=True))
    async def set_afk(event):
        global AFK_ON, AFK_REASON, AFK_START
        if AFK_ON:
            await event.respond("🟡 AFK is already enabled!")
            return
        AFK_REASON = event.raw_text.split(maxsplit=1)[1] if len(event.raw_text.split()) > 1 else "I am AFK"
        AFK_ON = True
        AFK_START = datetime.now()
        await event.respond(f"✅ I am now AFK: {AFK_REASON}")

    @client.on(events.NewMessage(outgoing=True))
    async def remove_afk(event):
        global AFK_ON, AFK_REASON, AFK_START
        # Ignore .afk message itself
        if event.raw_text.startswith('.afk'):
            return
        if AFK_ON:
            AFK_ON = False
            afk_time = int((datetime.now() - AFK_START).total_seconds())
            AFK_START = None
            await event.respond(f"✅ I am back online! AFK duration: {afk_time} seconds.")

    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        global AFK_ON, AFK_REASON, AFK_START
        if not AFK_ON:
            return

        # Only reply if DM or mentioned in group (and not from a bot)
        if not event.is_private and not getattr(event, "mentioned", False):
            return

        sender = await event.get_sender()
        if not sender or sender.bot:
            return

        duration = int((datetime.now() - AFK_START).total_seconds())
        try:
            await event.reply(f"⏳ I am currently AFK ({AFK_REASON})\nAway for {duration} seconds.")
        except Exception:
            pass
