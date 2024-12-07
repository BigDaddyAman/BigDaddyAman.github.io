from flask import Flask, request, jsonify
import logging
import sqlite3
from telethon import TelegramClient

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Your API ID, hash, and bot token obtained from https://my.telegram.org and BotFather
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'
bot_token = '7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0'
user_chat_id = 7951420571  # Replace with the actual user chat ID

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Connect to SQLite database
conn = sqlite3.connect('files.db')
c = conn.cursor()

@app.route('/send-video-link', methods=['POST'])
def send_video_link():
    data = request.json
    video_id = data.get('videoId')

    if not video_id:
        return jsonify({"success": False, "error": "Missing videoId"}), 400

    c.execute("SELECT id, access_hash, file_reference, mime_type, caption, file_name FROM files WHERE id=?", (video_id,))
    db_result = c.fetchone()

    if not db_result:
        return jsonify({"success": False, "error": "Video not found"}), 404

    id, access_hash, file_reference, mime_type, caption, file_name = db_result
    logging.debug(f"Sending video file: id={id}, access_hash={access_hash}, file_reference={file_reference}, mime_type={mime_type}, caption={caption}, file_name={file_name}")

    document = {
        "id": int(id),
        "access_hash": int(access_hash),
        "file_reference": file_reference,
        "mime_type": mime_type,
        "file_name": file_name
    }

    async def send_file():
        await client.send_file(user_chat_id, document, caption=caption, attributes=[DocumentAttributeFilename(file_name=file_name)] if file_name else None)

    client.loop.run_until_complete(send_file())

    return jsonify({"success": True, "message": "Video link sent!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
