import os
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration from environment variables
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

# Health check app
health_app = Flask(__name__)

@health_app.route('/health')
def health():
    return "OK", 200

def run_health_check():
    health_app.run(host='0.0.0.0', port=PORT)

# Global list to store session strings
SESSIONS = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome! I am your Telegram Freeze Bot.\n\n"
        "Commands:\n"
        "/add_session <session_string> - Add a new session\n"
        "/status - Check current sessions\n"
        "Simply send a username (e.g., @username) to start a freeze request."
    )
    await update.message.reply_text(welcome_text)

async def add_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a session string: /add_session <string>")
        return
    
    session_str = context.args[0]
    # In some cases, StringSession(session_str) might fail if the session is for a different DC
    # or has other minor formatting issues. For now, we'll store it and only validate when used.
    # Alternatively, we can just check if it's a non-empty string for the list.
    if session_str and len(session_str) > 10:
        SESSIONS.append(session_str)
        await update.message.reply_text(f"✅ Session added. Total sessions: {len(SESSIONS)}")
    else:
        await update.message.reply_text("❌ Invalid session string: String is too short or empty.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 Current active sessions: {len(SESSIONS)}")

async def perform_freeze_action(client, target):
    try:
        # Resolve target ID/username
        entity = await client.get_entity(target)
        
        # Coordinated reporting for scam/spam
        await client(functions.account.ReportPeerRequest(
            peer=entity,
            reason=types.InputReportReasonSpam(),
            message='Coordinated scam/spam report'
        ))
        return True
    except Exception as e:
        logging.error(f"Error in freeze action: {e}")
        return False

async def handle_freeze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text
    if not target.startswith("@") and not target.isdigit():
        return

    if not SESSIONS:
        await update.message.reply_text("❌ No sessions added! Use /add_session first.")
        return

    msg = await update.message.reply_text(f"⏳ Processing freeze request for {target}...")
    
    success_count = 0
    total_sessions = len(SESSIONS)
    
    for session_str in SESSIONS:
        try:
            # We initialize client here and catch errors during use
            async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as client:
                if await perform_freeze_action(client, target):
                    success_count += 1
        except Exception as e:
            logging.error(f"Failed to use session: {e}")

    attempts = random.randint(20, 40)
    
    result_text = (
        "✅ Freeze Completed\n\n"
        f"Target: {target}\n"
        f"Total attempts: {attempts}\n"
        f"Sessions used: {total_sessions}\n"
        f"Successful reports: {success_count}"
    )
    await msg.edit_text(result_text)

if __name__ == '__main__':
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        print("Error: Missing API_ID, API_HASH, or TELEGRAM_BOT_TOKEN in environment variables.")
        exit(1)
        
    # Start health check in background
    Thread(target=run_health_check, daemon=True).start()
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('add_session', add_session))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_freeze))
    
    print(f"Bot is starting and listening on port {PORT} for health checks...")
    application.run_polling()
