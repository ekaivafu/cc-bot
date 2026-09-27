import asyncio
import subprocess
import sys
import os
import json
import html
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ====== CONFIGURATION ======
# Reads token from environment variable BOT_TOKEN, or fallback to placeholder
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip() or "YOUR_TELEGRAM_BOT_TOKEN_HERE"
BRAINTREE_SCRIPT = os.path.join(os.path.dirname(__file__), "BRAINTREE_KILLER.py")
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Health check server for cloud hosting platforms like Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is online and healthy!")

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logging in console

def start_health_server():
    port = int(os.environ.get("PORT", "8080"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        print(f"[INFO] Health check server listening on 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"[WARNING] Health check server error: {e}")

# Load user IDs from file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

# Save user IDs to file
def save_users(user_ids):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(list(user_ids), f)

# Global set to store user IDs
user_ids = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_chat.id
    user_ids.add(user_id)
    save_users(user_ids)

    await update.message.reply_text(
        '👋 Hello! I am the CC Bot.\n\n'
        'Send me a command in the format:\n'
        '/cc ccnum|month|year|cvv\n\n'
        'Example: /cc 4111111111111111|12|2025|123'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_id = update.effective_chat.id
    user_ids.add(user_id)
    save_users(user_ids)

    await update.message.reply_text(
        '📝 Available commands:\n\n'
        '/start - Start the bot\n'
        '/help - Show this help message\n'
        '/cc ccnum|month|year|cvv - Process a card\n\n'
        'Example: /cc 4111111111111111|12|2025|123'
    )

async def cc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cc command."""
    user_id = update.effective_chat.id
    user_ids.add(user_id)
    save_users(user_ids)

    # Get the full message text
    text = update.message.text

    # Remove the '/cc ' prefix
    if not text.startswith('/cc '):
        await update.message.reply_text(
            '❌ Invalid command format. Use:\n'
            '/cc ccnum|month|year|cvv\n\n'
            'Example: /cc 4111111111111111|12|2025|123'
        )
        return

    # Extract the card info
    card_info = text[4:].strip()  # Remove '/cc ' prefix

    # Validate format
    if '|' not in card_info:
        await update.message.reply_text(
            '❌ Invalid format. Use:\n'
            '/cc ccnum|month|year|cvv\n\n'
            'Example: /cc 4111111111111111|12|2025|123'
        )
        return

    parts = card_info.split('|')
    if len(parts) != 4:
        await update.message.reply_text(
            '❌ Invalid format. Expected 4 parts: ccnum|month|year|cvv\n\n'
            'Example: /cc 4111111111111111|12|2025|123'
        )
        return

    card_number, exp_month, exp_year, cvv = parts

    # Basic validation
    if not card_number.isdigit() or len(card_number) < 13:
        await update.message.reply_text('❌ Invalid card number')
        return

    if not (exp_month.isdigit() and 1 <= int(exp_month) <= 12):
        await update.message.reply_text('❌ Invalid expiry month')
        return

    if not (exp_year.isdigit() and len(exp_year) == 4):
        await update.message.reply_text('❌ Invalid expiry year')
        return

    if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
        await update.message.reply_text('❌ Invalid CVV')
        return

    # Send processing message
    processing_msg = await update.message.reply_text('🔄 Processing your request...')

    try:
        # Run the BRAINTREE_KILLER script with the card parameters
        result = await run_braintree_script(card_number, exp_month, exp_year, cvv)

        # Send the full result safely formatted
        escaped_result = html.escape(result)
        if len(escaped_result) > 3500:
            await processing_msg.edit_text('✅ Processing complete! Sending detailed output...')
            chunks = [escaped_result[i:i+3500] for i in range(0, len(escaped_result), 3500)]
            for chunk in chunks:
                await update.message.reply_text(f'<pre>{chunk}</pre>', parse_mode='HTML')
        else:
            await processing_msg.edit_text(f'<pre>{escaped_result}</pre>', parse_mode='HTML')

    except Exception as e:
        await processing_msg.edit_text(f'❌ Error processing request:\n{str(e)}')

async def run_braintree_script(card_number, exp_month, exp_year, cvv):
    """Run the BRAINTREE_KILLER script with given parameters."""
    # Check if the script exists
    if not os.path.exists(BRAINTREE_SCRIPT):
        raise FileNotFoundError(f"BRAINTREE_KILLER.py not found at {BRAINTREE_SCRIPT}")

    # Prepare the input for the script
    # The script expects: card_number, exp_month, exp_year, cvv_real, zip_real
    # We'll provide a default ZIP code
    input_data = f"{card_number}\n{exp_month}\n{exp_year}\n{cvv}\n10000\n"

    try:
        # Run the script with the input data
        process = await asyncio.create_subprocess_exec(
            sys.executable, BRAINTREE_SCRIPT,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT  # Combine stderr with stdout
        )

        stdout, _ = await process.communicate(input=input_data.encode())

        if process.returncode != 0:
            # Even if return code is not zero, we might still have useful output
            output = stdout.decode().strip()
            if output:
                return output
            raise Exception(f"Script failed with return code {process.returncode}")

        return stdout.decode().strip()

    except Exception as e:
        raise Exception(f"Failed to run script: {str(e)}")

async def send_startup_message(application: Application) -> None:
    """Send a startup message to all known users."""
    if not user_ids:
        print("[INFO] No users to notify on startup")
        return

    print(f"[INFO] Sending startup message to {len(user_ids)} users...")
    message = "🤖 I am online and ready to process cards!"

    for user_id in user_ids:
        try:
            await application.bot.send_message(chat_id=user_id, text=message)
            print(f"[INFO] Sent startup message to user {user_id}")
        except Exception as e:
            print(f"[ERROR] Failed to send message to user {user_id}: {e}")

def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("[ERROR] BOT_TOKEN is not configured!")
        print("[ERROR] Please set the BOT_TOKEN environment variable in Render or update bot.py.")
        sys.exit(1)

    # Ensure an active asyncio event loop in MainThread (required for Python 3.12+ and 3.14)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Start health check server in background thread for Render
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cc", cc_command))

    # Run the bot until the user presses Ctrl-C
    print("[INFO] Bot is starting...")
    print(f"[INFO] Loaded {len(user_ids)} known users")

    # Send startup message after initializing the application
    async def post_init(app):
        await send_startup_message(app)

    application.post_init = post_init

    print("[INFO] Send commands to your bot on Telegram")
    application.run_polling()

if __name__ == "__main__":
    main()