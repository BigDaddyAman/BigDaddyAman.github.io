import sqlite3
import secrets
import logging
from telethon import TelegramClient, events

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Telegram API credentials
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'
bot_token = '7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0'

# Create SQLite database and connect
conn = sqlite3.connect("files.db", check_same_thread=False)
c = conn.cursor()

# Create table for file storage
c.execute("""
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    caption TEXT,
    file_name TEXT
)
""")
conn.commit()

# Initialize Telegram bot
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Store temporary link tokens
link_tokens = {}


@client.on(events.NewMessage)
async def handle_new_message(event):
    if event.file:
        # Save file details to the database
        file_id = event.file.id
        caption = event.raw_text
        file_name = event.file.name or "Unnamed File"
        c.execute("INSERT INTO files (id, caption, file_name) VALUES (?, ?, ?)", (file_id, caption, file_name))
        conn.commit()

        await event.reply(f"File '{file_name}' saved successfully! Use the search command to find files.")
    elif event.raw_text.lower().startswith('/search'):
        # Search for files based on user query
        query = event.raw_text[len('/search '):].strip()
        c.execute("SELECT id, file_name FROM files WHERE file_name LIKE ?", (f"%{query}%",))
        results = c.fetchall()

        if results:
            response = "Search Results:\n"
            for file_id, file_name in results:
                response += f"- {file_name}: [Get Link](https://t.me/yourbot?start={file_id})\n"
            await event.reply(response, link_preview=False)
        else:
            await event.reply("No files found matching your query.")


@client.on(events.CallbackQuery)
async def handle_callback_query(event):
    data = event.data.decode('utf-8')

    # Fetch file metadata from the database
    c.execute("SELECT id, caption, file_name FROM files WHERE id=?", (data,))
    db_result = c.fetchone()

    if db_result:
        id, caption, file_name = db_result

        # Generate a unique token
        token = secrets.token_urlsafe(16)
        link_tokens[token] = {'id': id, 'caption': caption, 'file_name': file_name, 'chat_id': event.chat_id}

        # Redirect user to the Netlify website
        web_link = f"https://kakifilem.netlify.app/get-link?token={token}"
        await event.reply(f"Click [here]({web_link}) to confirm and get the file.", link_preview=False)


if __name__ == "__main__":
    print("Bot is running...")
    client.run_until_disconnected()
