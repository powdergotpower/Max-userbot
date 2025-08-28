from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio

api_id = 22071176
api_hash = '7ed5401b625a0a4d3c45caf12c87f166'
string_session = '1BVtsOJoBu3iNN6Rz96Nwbll7dyrrzoVrKYyWhqtZxJUHSiFsN2XvEU3APCn7Bw5w9n_qfG9N47oP_0Sy-bS2ql4NqMnUEKoHa33Wg0kFYTjskpYL8LsBzgp90PUlYbnKA_vH7iI031GpquW3d1Il9kNr_amnO935Oc6PtsGIucUk3sDuWShwlTN2dnI7YbTAy8kQlFAmkcCNbIWAAvUGiWP7e41veGVTZTxCuH8PebQjKXZdG_xGyxm_yf-WqMbWacHDbT9XMWndcKyAbdLBZsNfCL0xaCEBY30hNBWL30L2o8eOwlY1HiNlEXiBRo09ZYx3Cv4lQeDYkbnMs1M6fDx0NMdXi4c='  # Paste your string session here

client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage(pattern=r'\.alive'))
async def handler(event):
    # Edit the message that triggered the event
    await event.edit('I am alive')

async def main():
    await client.start()
    print("Userbot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
