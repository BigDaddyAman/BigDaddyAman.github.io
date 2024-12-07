import logging
import sqlite3
from flask import Flask, request, jsonify
from telethon import TelegramClient, events, Button
from telethon.tl.types import Document, DocumentAttributeFilename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Your API ID, hash, and bot token obtained from https://my.telegram.org and BotFather
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'
bot_token = '7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0'
user_chat_id = 7951420571  # Replace with the actual user chat ID

# Initialize Telegram client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Initialize Flask app
app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('files.db', check_same_thread=False)
c = conn.cursor()

# Ensure the table to store file metadata exists
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id TEXT PRIMARY KEY, access_hash TEXT, file_reference BLOB, mime_type TEXT, caption TEXT, keywords TEXT, file_name TEXT)''')
conn.commit()

@app.route('/send-video-link', methods=['POST'])
def send_video_link():
    try:
        data = request.json
        video_id = data.get('videoId')
        logging.debug(f"Received video ID: {video_id}")

        if not video_id:
            logging.error("Missing video ID")
            return jsonify({"success": False, "error": "Missing videoId"}), 400

        c.execute("SELECT id, access_hash, file_reference, mime_type, caption, file_name FROM files WHERE id=?", (video_id,))
        db_result = c.fetchone()
        logging.debug(f"Database result: {db_result}")

        if not db_result:
            logging.error("Video not found")
            return jsonify({"success": False, "error": "Video not found"}), 404

        id, access_hash, file_reference, mime_type, caption, file_name = db_result
        logging.debug(f"Preparing to send video file: {file_name}")

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

        async def send_file():
            await client.send_file(user_chat_id, document, caption=caption, attributes=[DocumentAttributeFilename(file_name=file_name)] if file_name else None)

        client.loop.run_until_complete(send_file())

        logging.debug("Video link sent successfully")
        return jsonify({"success": True, "message": "Video link sent!"}), 200
    except Exception as e:
        logging.error(f"Error handling request: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
