@client.on(events.NewMessage(incoming=True))
async def afk_reply(event):
    global AFK, AFK_REASON, AFK_START, MESSAGES, REPLIED_USERS
    if not AFK or AFK_START is None or event.out:
        return
    if not event.is_private:  # Only PM
        return

    sender = await event.get_sender()
    if not sender:
        return
    sender_name = sender.first_name
    sender_id = sender.id

    # Only reply once per user
    if sender_id in REPLIED_USERS:
        return
    REPLIED_USERS.add(sender_id)

    # Count messages
    MESSAGES[sender_name] = MESSAGES.get(sender_name, 0) + 1

    afk_time = int(time.time() - AFK_START)
    await event.reply(f"⏳ I am AFK ({AFK_REASON})\nAway for {afk_time} sec")
