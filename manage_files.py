import logging
import sqlite3
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, Document, DocumentAttributeFilename, InputTextMessageContent, InlineQueryResultDocument

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

# Clear existing entries and create table to store file metadata
c.execute('DROP TABLE IF EXISTS files')
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id TEXT, access_hash TEXT, file_reference BLOB, mime_type TEXT, caption TEXT, keywords TEXT, file_name TEXT)''')
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
        if isinstance(event.message.peer_id, PeerUser):
            if event.message.document:
                document = event.message.document
                file_name = None
                for attr in event.message.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        file_name = attr.file_name
                        break

                caption = event.message.message or ""
                keywords = caption.split()  # Simple keyword extraction; refine as needed

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
                logging.debug(f"Inserting file metadata: id={id}, access_hash={access_hash}, file_reference={file_reference}, mime_type={mime_type}, caption={caption}, keywords={' '.join(keywords)}, file_name={file_name}")
                c.execute("INSERT INTO files (id, access_hash, file_reference, mime_type, caption, keywords, file_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (id, access_hash, file_reference, mime_type, caption, ' '.join(keywords), file_name))
                conn.commit()
                await event.reply('File metadata stored.')

    @client.on(events.InlineQuery)
    async def inline_query_handler(event):
        query = event.query.query.strip().lower()
        logging.debug(f"Received inline query: {query}")
        results = []

        # Search database for matching files
        c.execute("SELECT id, access_hash, file_reference, mime_type, caption, file_name FROM files WHERE keywords LIKE ?", (f'%{query}%',))
        db_results = c.fetchall()
        logging.debug(f"Database search results: {db_results}")

        # Populate inline results from the database
        for id, access_hash, file_reference, mime_type, caption, file_name in db_results:
            logging.debug(f"Adding to inline results: id={id}, caption={caption}, file_name={file_name}")
            results.append(
                InlineQueryResultDocument(
                    id=str(id),
                    title=caption,
                    document_file_id=file_reference,
                    mime_type=mime_type,
                    description=caption,
                    caption=caption,
                    input_message_content=InputTextMessageContent(caption),
                )
            )

        logging.debug(f"Inline query results: {results}")
        await event.answer(results, cache_time=0, is_personal=True)

    @client.on(events.NewMessage(pattern='/listdb'))
    async def list_db(event):
        # List all entries in the database for debugging
        logging.debug("Executing /listdb command")
        c.execute("SELECT * FROM files")
        results = c.fetchall()
        logging.debug(f"Database entries: {results}")
        await event.reply(f"Database entries: {results}")

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
