import logging
import sqlite3
from telethon import TelegramClient, events, Button
from telethon.tl.types import Document, DocumentAttributeFilename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Your API ID, hash, and bot token obtained from https://my.telegram.org and BotFather
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'
bot_token = '7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Connect to SQLite database
conn = sqlite3.connect('files.db')
c = conn.cursor()

# Ensure the table to store file metadata exists
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id TEXT PRIMARY KEY, access_hash TEXT, file_reference BLOB, mime_type TEXT, caption TEXT, keywords TEXT, file_name TEXT)''')
conn.commit()

VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.webm', '.ts', '.mov', '.avi', '.flv', '.wmv', '.m4v', '.mpeg', '.mpg', '.3gp', '.3g2']

async def main():
    await client.start()
    print("Client created")

    @client.on(events.NewMessage)
    async def handle_messages(event):
        if event.is_private:
            if event.message.text:
                text = event.message.text.lower().strip()
                logging.debug(f"Received text message: {text}")

                c.execute("SELECT id, caption, file_name FROM files WHERE keywords LIKE ?", (f'%{text}%',))
                db_results = c.fetchall()
                logging.debug(f"Database search results for keyword '{text}': {db_results}")

                video_results = [result for result in db_results if any(result[2].lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]
                logging.debug(f"Filtered video results: {video_results}")

                if video_results:
                    buttons = [
                        [Button.inline(file_name or caption or "Unknown File", f"http://your-site.com/get-link?videoId={id}")]
                        for id, caption, file_name in video_results
                    ]
                    logging.debug(f"Generated buttons: {buttons}")
                    await event.respond('Select a video file:', buttons=buttons)
                else:
                    logging.debug(f"No matching video files found for keyword '{text}'.")
                    await event.reply('No matching video files found.')

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
