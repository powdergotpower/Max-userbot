from telethon import events
import time

# Global AFK state
AFK = False
AFK_REASON = None
AFK_START = None
MESSAGES = {}
REPLIED_USERS = set()


def register(client):
    # Command to set AFK
    @client.on(events.NewMessage(pattern=r'\.afk'))
    async def set_afk(event):
        global AFK, AFK_REASON, AFK_START, MESSAGES, REPLIED_USERS
        args = event.raw_text.split(maxsplit=1)
        AFK_REASON = args[1] if len(args) > 1 else "AFK"
        AFK = True
        AFK_START = time.time()
        MESSAGES.clear()
        REPLIED_USERS.clear()
        await event.edit(f"✅ I am now AFK: {AFK_REASON}")

    # Remove AFK on any outgoing message
    @client.on(events.NewMessage(outgoing=True))
    async def remove_afk(event):
        global AFK, AFK_REASON, AFK_START, MESSAGES, REPLIED_USERS
        if AFK:
            AFK = False
            AFK_REASON = None
            afk_time = int(time.time() - AFK_START) if AFK_START else 0
            AFK_START = None
            REPLIED_USERS.clear()
            msg = f"✅ I am back online! You were AFK for {afk_time} seconds."
            await event.edit(msg)
            # Notify who messaged you
            if MESSAGES:
                summary = "People who messaged you while AFK:\n"
                for user, count in MESSAGES.items():
                    summary += f"- {user}: {count} message(s)\n"
                await event.respond(summary)
                MESSAGES.clear()

    # Auto-reply to incoming messages (robust for userbot)
    @client.on(events.NewMessage())
    async def afk_reply(event):
        global AFK, AFK_REASON, AFK_START, MESSAGES, REPLIED_USERS

        if not AFK or AFK_START is None or event.out:
            return

        # Only reply in private chats with real users
        if not getattr(event.chat, "megagroup", False) and event.is_private:
            sender = await event.get_sender()
            if not sender:
                return
            sender_id = sender.id
            sender_name = sender.first_name

            if sender_id in REPLIED_USERS:
                return
            REPLIED_USERS.add(sender_id)

            MESSAGES[sender_name] = MESSAGES.get(sender_name, 0) + 1
            afk_time = int(time.time() - AFK_START)
            await event.reply(f"⏳ I am currently AFK ({AFK_REASON})\nAway for {afk_time} sec")
