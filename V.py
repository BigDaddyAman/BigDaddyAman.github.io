import logging
import sqlite3
from telethon import TelegramClient, events, Button
from telethon.tl.types import PeerUser, Document, DocumentAttributeFilename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Your API ID and hash obtained from https://my.telegram.org
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'

# Your phone number
phone_number = '+60128479187'

client = TelegramClient('session_name', api_id, api_hash)

# Connect to SQLite database
conn = sqlite3.connect('files.db')
c = conn.cursor()

# Ensure the table to store file metadata exists
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id TEXT PRIMARY KEY, access_hash TEXT, file_reference BLOB, mime_type TEXT, caption TEXT, keywords TEXT, file_name TEXT)''')
conn.commit()

async def main():
    await client.start()
    print("Client created")

    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input('Enter the code: ')
        await client.sign_in(phone_number, code)

    @client.on(events.NewMessage)
    async def handle_messages(event):
        # Ensure the bot only responds to private messages
        if event.is_private:
            sender = await event.get_sender()
            if sender and sender.id == (await client.get_me()).id:
                if event.message.document:
                    document = event.message.document
                    file_name = None
                    for attr in event.message.document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name
                            break

                    caption = event.message.message or ""
                    keywords = f"{caption.lower()} {file_name.lower()}"  # Combine caption and file name as keywords

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
                    # Check if message contains a slash command and ignore it
                    if event.message.text.startswith('/'):
                        logging.debug(f"Ignoring command: {event.message.text}")
                        return

                    # Check if message contains a keyword and respond with a list of options
                    text = event.message.text.lower().strip()
                    logging.debug(f"Received text message: {text}")

                    c.execute("SELECT id, caption, file_name FROM files WHERE keywords LIKE ?", (f'%{text}%',))
                    db_results = c.fetchall()
                    logging.debug(f"Database search results for keyword '{text}': {db_results}")

                    if db_results:
                        buttons = [
                            [Button.inline(file_name or caption or "Unknown File", data=str(id))]
                            for id, caption, file_name in db_results
                        ]
                        logging.debug(f"Generated buttons: {buttons}")
                        await event.respond('Select a file:', buttons=buttons)
                    else:
                        logging.debug(f"No matching files found for keyword '{text}'.")
                        await event.reply('No matching files found.')

    @client.on(events.CallbackQuery)
    async def callback_query_handler(event):
        data = event.data.decode('utf-8')
        logging.debug(f"Callback query data: {data}")

        # Fetch the document metadata from the database
        c.execute("SELECT id, access_hash, file_reference, mime_type, caption, file_name FROM files WHERE id=?", (data,))
        db_result = c.fetchone()
        logging.debug(f"Database fetch result: {db_result}")

        if db_result:
            id, access_hash, file_reference, mime_type, caption, file_name = db_result
            logging.debug(f"Sending file: id={id}, access_hash={access_hash}, file_reference={file_reference}, mime_type={mime_type}, caption={caption}, file_name={file_name}")

            # Recreate Document object
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

    @client.on(events.NewMessage(pattern='/listdb'))
    async def list_db(event):
        # List all entries in the database for debugging
        logging.debug("Executing /listdb command")
        c.execute("SELECT * FROM files")
        results = c.fetchall()
        logging.debug(f"Database entries: {results}")
        await event.reply(f"Database entries: {results}")

    @client.on(events.NewMessage(pattern='/deletedb'))
    async def delete_db(event):
        # Delete all entries from the database
        logging.debug("Executing /deletedb command")
        c.execute("DELETE FROM files")
        conn.commit()
        logging.debug("All entries deleted from the database")
        await event.reply("All entries deleted from the database.")

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
