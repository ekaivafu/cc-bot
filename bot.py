# =========================================================
# 👑 DEVELOPER TELEGRAM: @tgekaiva
# 👑 PROJECT: CC BOT (TELEGRAM BOT FOR RENDER)
# 👑 AUTHOR / DEV: @tgekaiva
# =========================================================

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
# Developer Telegram: @tgekaiva - Configuration settings
DEV_WATERMARK = "\n\n👑 Developer Telegram: @tgekaiva"
DEV_WATERMARK_HTML = "\n\n👑 <b>Developer:</b> @tgekaiva"

# Reads token from environment variable BOT_TOKEN, or fallback to placeholder
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip() or "YOUR_TELEGRAM_BOT_TOKEN_HERE"
BRAINTREE_SCRIPT = os.path.join(os.path.dirname(__file__), "BRAINTREE_KILLER.py")
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Developer Telegram: @tgekaiva - Health check server for cloud hosting platforms like Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is online and healthy! Dev: @tgekaiva")

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logging in console

# Developer Telegram: @tgekaiva - Start HTTP health server for Render Free Web Service
def start_health_server():
    port = int(os.environ.get("PORT", "8080"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        print(f"[INFO] Health check server listening on 0.0.0.0:{port} | Dev: @tgekaiva")
        server.serve_forever()
    except Exception as e:
        print(f"[WARNING] Health check server error: {e}")

# Developer Telegram: @tgekaiva - Load user IDs from file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

# Developer Telegram: @tgekaiva - Save user IDs to file
def save_users(user_ids):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(list(user_ids), f)

# Global set to store user IDs
user_ids = load_users()

# Developer Telegram: @tgekaiva - /start command handler
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
        f'{DEV_WATERMARK}'
    )

# Developer Telegram: @tgekaiva - /help command handler
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
        f'{DEV_WATERMARK}'
    )

# Developer Telegram: @tgekaiva - /cc command handler
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
            f'{DEV_WATERMARK}'
        )
        return

    # Extract the card info
    card_info = text[4:].strip()

    # Validate format
    if '|' not in card_info:
        await update.message.reply_text(
            '❌ Invalid format. Use:\n'
            '/cc ccnum|month|year|cvv\n\n'
            'Example: /cc 4111111111111111|12|2025|123'
            f'{DEV_WATERMARK}'
        )
        return

    parts = card_info.split('|')
    if len(parts) != 4:
        await update.message.reply_text(
            '❌ Invalid format. Expected 4 parts: ccnum|month|year|cvv\n\n'
            'Example: /cc 4111111111111111|12|2025|123'
            f'{DEV_WATERMARK}'
        )
        return

    card_number, exp_month, exp_year, cvv = parts

    # Basic validation
    if not card_number.isdigit() or len(card_number) < 13:
        await update.message.reply_text(f'❌ Invalid card number{DEV_WATERMARK}')
        return

    if not (exp_month.isdigit() and 1 <= int(exp_month) <= 12):
        await update.message.reply_text(f'❌ Invalid expiry month{DEV_WATERMARK}')
        return

    if not (exp_year.isdigit() and len(exp_year) == 4):
        await update.message.reply_text(f'❌ Invalid expiry year{DEV_WATERMARK}')
        return

    if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
        await update.message.reply_text(f'❌ Invalid CVV{DEV_WATERMARK}')
        return

    # Send processing message
    processing_msg = await update.message.reply_text(f'🔄 Processing your request...{DEV_WATERMARK}')

    try:
        # Run the BRAINTREE_KILLER script with the card parameters
        result = await run_braintree_script(card_number, exp_month, exp_year, cvv)

        # Developer Telegram: @tgekaiva - Safely format result with developer watermark
        escaped_result = html.escape(result)
        if len(escaped_result) > 3500:
            await processing_msg.edit_text(f'✅ Processing complete! Sending detailed output...{DEV_WATERMARK_HTML}', parse_mode='HTML')
            chunks = [escaped_result[i:i+3500] for i in range(0, len(escaped_result), 3500)]
            for chunk in chunks:
                await update.message.reply_text(f'<pre>{chunk}</pre>{DEV_WATERMARK_HTML}', parse_mode='HTML')
        else:
            await processing_msg.edit_text(f'<pre>{escaped_result}</pre>{DEV_WATERMARK_HTML}', parse_mode='HTML')

    except Exception as e:
        await processing_msg.edit_text(f'❌ Error processing request:\n{str(e)}{DEV_WATERMARK}')

# Developer Telegram: @tgekaiva - Run BRAINTREE_KILLER script
async def run_braintree_script(card_number, exp_month, exp_year, cvv):
    """Run the BRAINTREE_KILLER script with given parameters."""
    if not os.path.exists(BRAINTREE_SCRIPT):
        raise FileNotFoundError(f"BRAINTREE_KILLER.py not found at {BRAINTREE_SCRIPT}")

    # Prepare input for script
    input_data = f"{card_number}\n{exp_month}\n{exp_year}\n{cvv}\n10000\n"

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, BRAINTREE_SCRIPT,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        stdout, _ = await process.communicate(input=input_data.encode())

        if process.returncode != 0:
            output = stdout.decode().strip()
            if output:
                return output
            raise Exception(f"Script failed with return code {process.returncode}")

        return stdout.decode().strip()

    except Exception as e:
        raise Exception(f"Failed to run script: {str(e)}")

# Developer Telegram: @tgekaiva - Startup notification to users
async def send_startup_message(application: Application) -> None:
    """Send a startup message to all known users."""
    if not user_ids:
        print("[INFO] No users to notify on startup | Dev: @tgekaiva")
        return

    print(f"[INFO] Sending startup message to {len(user_ids)} users... | Dev: @tgekaiva")
    message = f"🤖 I am online and ready to process cards!{DEV_WATERMARK}"

    for user_id in user_ids:
        try:
            await application.bot.send_message(chat_id=user_id, text=message)
            print(f"[INFO] Sent startup message to user {user_id}")
        except Exception as e:
            print(f"[ERROR] Failed to send message to user {user_id}: {e}")

# Developer Telegram: @tgekaiva - Main entry point
def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("[ERROR] BOT_TOKEN is not configured!")
        print("[ERROR] Please set the BOT_TOKEN environment variable in Render or update bot.py.")
        print("[INFO] Developer Telegram: @tgekaiva")
        sys.exit(1)

    # Developer Telegram: @tgekaiva - Ensure event loop exists for Python 3.12+ and 3.14
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Developer Telegram: @tgekaiva - Start background health check server
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Developer Telegram: @tgekaiva - Build Telegram Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cc", cc_command))

    print("[INFO] Bot is starting... | Developer Telegram: @tgekaiva")
    print(f"[INFO] Loaded {len(user_ids)} known users")

    # Send startup message after initializing the application
    async def post_init(app):
        await send_startup_message(app)

    application.post_init = post_init

    print("[INFO] Send commands to your bot on Telegram | Developer: @tgekaiva")
    application.run_polling()

if __name__ == "__main__":
    main()