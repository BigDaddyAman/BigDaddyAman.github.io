from flask import Flask, request, jsonify
from telethon import TelegramClient

app = Flask(__name__)

# Telegram API credentials
api_id = 24492108
api_hash = '82342323c63f78f9b0bc7a3ecd7c2509'
bot_token = '7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0'

# Telegram bot client
bot_client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Link tokens from the bot
link_tokens = {}


@app.route('/api/send-file', methods=['POST'])
def send_file():
    token = request.args.get('token')
    if not token or token not in link_tokens:
        return jsonify({"error": "Invalid or expired token."}), 400

    # Retrieve file data from token
    file_data = link_tokens.pop(token)
    chat_id = file_data['chat_id']
    caption = file_data['caption']
    file_name = file_data['file_name']
    file_id = file_data['id']

    # Send the file to the user via Telegram bot
    with bot_client:
        bot_client.loop.run_until_complete(
            bot_client.send_file(
                chat_id,
                file=file_id,
                caption=caption or f"Here is your file: {file_name}"
            )
        )

    return jsonify({"message": "File sent successfully."}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
