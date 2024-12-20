import logging
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the bot
TOKEN = "7775691173:AAG1r6loQFtl3AuPJKhMOXuyvXUrlDnmH98"
bot = Bot(token=TOKEN)
ADMIN_CHAT_ID = 7951420571  # Your actual chat ID

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for the app

# Ensure there's an existing event loop to use
loop = asyncio.get_event_loop()

async def send_report_message(message):
    try:
        logger.info(f"Attempting to send message to bot: {message}")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"New report received: {message}")
        logger.info("Message sent successfully to the bot.")
    except Exception as e:
        logger.error(f"Failed to send message to bot: {e}")

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    message = data.get('message')
    if message:
        loop.create_task(send_report_message(message))  # Use the existing event loop
        return jsonify({"status": "success", "message": "Report sent"}), 200
    return jsonify({"status": "error", "message": "No message found"}), 400

def start_flask_app():
    app.run(host='0.0.0.0', port=5000)

# Define the start command handler for the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! I am your reporting bot. Send me reports here or through the website.')

# Define a handler for any text message
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    await update.message.reply_text(f'Received your message: {text}')

def main() -> None:
    # Start Flask app in a separate thread
    threading.Thread(target=start_flask_app).start()

    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Register a message handler for any text message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
