from telethon import events, functions, types

def register(client):
    # -----------------------------
    # Kick command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.kick(?: |$)(.*)'))
    async def kick_user(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        args = event.pattern_match.group(1).strip()
        user = None
        if event.is_reply:
            user = await event.get_reply_user()
        elif args:
            try:
                user = await client.get_entity(args)
            except:
                return await event.reply("Invalid username or ID.")
        else:
            return await event.reply("Reply to a user or provide a username to kick.")

        try:
            await client.kick_participant(await event.get_chat(), user)
            await event.reply(f"👢 Kicked [{user.first_name}](tg://user?id={user.id})")
        except Exception as e:
            await event.reply(f"Error: {e}")

    # -----------------------------
    # Ban command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.ban(?: |$)(.*)'))
    async def ban_user(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        args = event.pattern_match.group(1).strip()
        user = None
        if event.is_reply:
            user = await event.get_reply_user()
        elif args:
            try:
                user = await client.get_entity(args)
            except:
                return await event.reply("Invalid username or ID.")
        else:
            return await event.reply("Reply to a user or provide a username to ban.")

        try:
            await client.edit_permissions(await event.get_chat(), user, view_messages=False)
            await event.reply(f"🚫 Banned [{user.first_name}](tg://user?id={user.id})")
        except Exception as e:
            await event.reply(f"Error: {e}")

    # -----------------------------
    # Unban command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.unban(?: |$)(.*)'))
    async def unban_user(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        args = event.pattern_match.group(1).strip()
        user = None
        if event.is_reply:
            user = await event.get_reply_user()
        elif args:
            try:
                user = await client.get_entity(args)
            except:
                return await event.reply("Invalid username or ID.")
        else:
            return await event.reply("Reply to a user or provide a username to unban.")

        try:
            await client.edit_permissions(await event.get_chat(), user, view_messages=True)
            await event.reply(f"✅ Unbanned [{user.first_name}](tg://user?id={user.id})")
        except Exception as e:
            await event.reply(f"Error: {e}")

    # -----------------------------
    # Pin command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.pin'))
    async def pin_message(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        if event.is_reply:
            reply = await event.get_reply_message()
            await client(functions.messages.PinMessageRequest(
                peer=await event.get_chat(),
                id=reply.id,
                silent=True
            ))
            await event.reply("📌 Pinned message")
        else:
            await event.reply("Reply to a message to pin.")

    # -----------------------------
    # Unpin command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.unpin'))
    async def unpin_message(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        chat = await event.get_chat()
        await client(functions.messages.UnpinAllMessagesRequest(peer=chat))
        await event.reply("📌 Unpinned all messages")

    # -----------------------------
    # Clean messages command
    # -----------------------------
    @client.on(events.NewMessage(pattern=r'\.clean(?: |$)(\d+)'))
    async def clean_messages(event):
        if not event.is_group:
            return await event.reply("This command only works in groups.")
        count = int(event.pattern_match.group(1) or 0)
        if count <= 0:
            return await event.reply("Provide a valid number of messages to delete.")
        messages = []
        async for msg in client.iter_messages(await event.get_chat(), limit=count + 1):
            messages.append(msg.id)
        await client.delete_messages(await event.get_chat(), messages)
        await event.reply(f"🧹 Cleaned last {count} messages.", delete_in=5)

    print("[+] admin.py loaded")
