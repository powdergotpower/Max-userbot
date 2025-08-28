from telethon import events
from datetime import datetime
import asyncio

# Global AFK state
class AFKState:
    def __init__(self):
        self.afk_on = False
        self.reason = None
        self.start_time = None
        self.last_afk_messages = {}  # chat_id: message
        self.replied_users = set()

AFK_ = AFKState()


def register(client):
    # Command to go AFK
    @client.on(events.NewMessage(pattern=r'\.afk'))
    async def set_afk(event):
        args = event.raw_text.split(maxsplit=1)
        AFK_.reason = args[1] if len(args) > 1 else "AFK"
        AFK_.afk_on = True
        AFK_.start_time = datetime.now()
        AFK_.last_afk_messages.clear()
        AFK_.replied_users.clear()
        await event.respond(f"✅ I am now AFK: {AFK_.reason}")

    # Remove AFK on any outgoing message
    @client.on(events.NewMessage(outgoing=True))
    async def remove_afk(event):
        if not AFK_.afk_on:
            return
        AFK_.afk_on = False
        afk_duration = (datetime.now() - AFK_.start_time).seconds
        AFK_.start_time = None
        AFK_.replied_users.clear()

        msg = f"✅ I am back online! You were AFK for {afk_duration} seconds."
        await event.respond(msg)

        # Clean up old AFK messages
        for m in AFK_.last_afk_messages.values():
            try:
                await m.delete()
            except Exception:
                pass
        AFK_.last_afk_messages.clear()

    # Auto-reply to incoming PMs while AFK
    @client.on(events.NewMessage())
    async def afk_reply(event):
        if not AFK_.afk_on or event.out:
            return

        # Only reply in private chats
        if event.is_private:
            sender = await event.get_sender()
            if not sender:
                return
            sender_id = sender.id
            chat_id = event.chat_id

            # Reply only once per user
            if sender_id in AFK_.replied_users:
                return
            AFK_.replied_users.add(sender_id)

            afk_duration = int((datetime.now() - AFK_.start_time).total_seconds())
            msg = await event.respond(
                f"⏳ I am currently AFK ({AFK_.reason})\nAway for {afk_duration} sec"
            )

            # Delete previous AFK message in this chat to avoid clutter
            if chat_id in AFK_.last_afk_messages:
                try:
                    await AFK_.last_afk_messages[chat_id].delete()
                except Exception:
                    pass

            AFK_.last_afk_messages[chat_id] = msg
