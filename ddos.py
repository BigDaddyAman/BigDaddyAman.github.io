import logging
import sqlite3
from telethon import TelegramClient, events, Button
from telethon.tl.types import Document, DocumentAttributeFilename
import requests

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

CAPTCHA_URL = 'https://your-captcha-site.com/verify?file_id='

async def main():
    await client.start()
    print("Client created")

    @client.on(events.NewMessage)
    async def handle_messages(event):
        if event.is_private:
            if event.message.document:
                document = event.message.document
                file_name = None
                for attr in event.message.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        file_name = attr.file_name
                        break

                caption = event.message.message or ""
                keywords = f"{caption.lower()} {file_name.lower()}"

                logging.debug(f"Received document message: {event.message}")
                logging.debug(f"Caption: {caption}")
                logging.debug(f"Keywords: {keywords}")
                logging.debug(f"File Name: {file_name}")
                logging.debug(f"Mime Type: {document.mime_type}")

                # Store necessary metadata
                id = document.id
                access_hash = document.access_hash
                file_reference = document.file_reference
                mime_type = document.mime_type

                # Insert file metadata into database
                logging.debug(f"Inserting file metadata: id={id}, access_hash={access_hash}, file_reference={file_reference}, mime_type={mime_type}, caption={caption}, keywords={keywords}, file_name={file_name}")
                c.execute("REPLACE INTO files (id, access_hash, file_reference, mime_type, caption, keywords, file_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (id, access_hash, file_reference, mime_type, caption, keywords, file_name))
                conn.commit()
                await event.reply('File metadata stored.')

            elif event.message.text:
                if event.message.text.startswith('/'):
                    logging.debug(f"Ignoring command: {event.message.text}")
                    return

                text = event.message.text.lower().strip()
                logging.debug(f"Received text message: {text}")

                c.execute("SELECT id, caption, file_name FROM files WHERE keywords LIKE ?", (f'%{text}%',))
                db_results = c.fetchall()
                logging.debug(f"Database search results for keyword '{text}': {db_results}")

                video_results = [result for result in db_results if any(result[2].lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]
                logging.debug(f"Filtered video results: {video_results}")

                if video_results:
                    buttons = [
                        [Button.inline(file_name or caption or "Unknown File", data=f'{CAPTCHA_URL}{id}')]
                        for id, caption, file_name in video_results
                    ]
                    logging.debug(f"Generated buttons: {buttons}")
                    await event.respond('Select a video file:', buttons=buttons)
                else:
                    logging.debug(f"No matching video files found for keyword '{text}'.")
                    await event.reply('No matching video files found.')

    @client.on(events.CallbackQuery)
    async def callback_query_handler(event):
        data = event.data.decode('utf-8')
        logging.debug(f"Callback query data: {data}")

        # Simulate CAPTCHA verification
        response = requests.get(data)  # Assuming the CAPTCHA URL returns the file ID on success
        if response.status_code == 200:
            file_id = response.text
            c.execute("SELECT id, access_hash, file_reference, mime_type, caption, file_name FROM files WHERE id=?", (file_id,))
            db_result = c.fetchone()
            logging.debug(f"Database fetch result: {db_result}")

            if db_result:
                id, access_hash, file_reference, mime_type, caption, file_name = db_result
                logging.debug(f"Sending video file: id={id}, access_hash={access_hash}, file_reference={file_reference}, mime_type={mime_type}, caption={caption}, file_name={file_name}")

                document = Document(
                    id=int(id),
                    access_hash=int(access_hash),
                    file_reference=file_reference,
                    date=None,
                    mime_type=mime_type,
                    size=None,
                    dc_id=None,
                    attributes=[]
                )

                await client.send_file(event.chat_id, document, caption=caption, attributes=[DocumentAttributeFilename(file_name=file_name)] if file_name else None)
        else:
            await event.reply("CAPTCHA verification failed. Please try again.")

    @client.on(events.NewMessage(pattern='/listdb'))
    async def list_db(event):
        logging.debug("Executing /listdb command")
        c.execute("SELECT * FROM files")
        results = c.fetchall()
        logging.debug(f"Database entries: {results}")
        await event.reply(f"Database entries: {results}")

    @client.on(events.NewMessage(pattern='/deletedb'))
    async def delete_db(event):
        logging.debug("Executing /deletedb command")
        c.execute("DELETE FROM files")
        conn.commit()
        logging.debug("All entries deleted from the database")
        await event.reply("All entries deleted from the database.")

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
