# modules/approve.py
import os
import json
from telethon import events
from main import client   # ✅ import the client from main.py

APPROVED_PATH = "approved.json"
PM_GUARD_TEXT = (
    "👋 Hey! My DMs are protected.\n\n"
    "🤝 If my master knows you, you’ll be approved soon.\n"
    "🚫 Please don’t spam or you’ll get blocked.\n\n"
    "— Powered by PM Guard"
)

# ---- File helpers ----
def load_approved():
    if not os.path.exists(APPROVED_PATH):
        return set()
    try:
        with open(APPROVED_PATH, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_approved(data: set):
    with open(APPROVED_PATH, "w") as f:
        json.dump(list(data), f)

APPROVED = load_approved()
WARNED_ONCE = set()

# ---- Auto-guard: reply to unknown PMs ----
@client.on(events.NewMessage(incoming=True))
async def pm_guard(event):
    if not event.is_private or (await event.get_sender()).is_self:
        return

    uid = event.sender_id
    if uid in APPROVED:
        return

    if uid not in WARNED_ONCE:
        WARNED_ONCE.add(uid)
        try:
            await event.reply(PM_GUARD_TEXT)
        except:
            pass

# ---- .apr command ----
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.apr(?:\s+(.*))?$"))
async def approve_cmd(event):
    if not event.is_private:
        return await event.edit("❗ Use `.apr` only inside the user's DM.")
    uid = event.chat_id
    reason = (event.pattern_match.group(1) or "").strip()

    if uid in APPROVED:
        return await event.edit("✅ Already approved to DM.")
    APPROVED.add(uid)
    save_approved(APPROVED)

    msg = "✅ Approved to DM."
    if reason:
        msg += f"\n📝 Reason: {reason}"
    await event.edit(msg)

# ---- .dis command ----
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.dis$"))
async def disapprove_cmd(event):
    if not event.is_private:
        return await event.edit("❗ Use `.dis` only inside the user's DM.")
    uid = event.chat_id

    if uid not in APPROVED:
        return await event.edit("ℹ️ This user wasn’t approved.")
    APPROVED.remove(uid)
    save_approved(APPROVED)
    WARNED_ONCE.discard(uid)
    await event.edit("🚫 Disapproved. They’ll see guard messages again.")

# ---- .approvedlist command ----
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.approvedlist$"))
async def approved_list_cmd(event):
    if not APPROVED:
        return await event.edit("📭 No approved users yet.")
    lines = []
    for uid in list(APPROVED)[:50]:
        lines.append(f"- [user](tg://user?id={uid})")
    extra = ""
    if len(APPROVED) > 50:
        extra = f"\n… and {len(APPROVED)-50} more"
    await event.edit("✅ **Approved users**:\n" + "\n".join(lines) + extra)
