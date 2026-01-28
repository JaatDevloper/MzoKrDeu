# Telegram Freeze Bot

## Overview

A Telegram bot built with Python that manages multiple Telegram sessions. The bot allows users to add session strings and perform "freeze" operations on target Telegram accounts. It uses both the python-telegram-bot library for the bot interface and Telethon for Telegram client functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **python-telegram-bot**: Handles the bot interface, command processing, and message handling using the ApplicationBuilder pattern
- **Telethon**: Provides Telegram client functionality for session management and advanced operations

### Command Structure
- `/start` - Welcome message and command list
- `/add_session <session_string>` - Add new Telegram sessions
- `/status` - Check number of active sessions
- Message handler for usernames (@username) to trigger freeze requests

### Session Management
- Sessions stored in a global list (in-memory storage)
- Session strings are Telethon session identifiers
- **Note**: Current implementation lacks persistence - sessions are lost on restart. A database solution should be added for production use.

### Configuration
All sensitive configuration uses environment variables:
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `TELEGRAM_BOT_TOKEN` - Bot token from BotFather

### Async Architecture
The application is fully asynchronous using Python's asyncio, which is required for both python-telegram-bot and Telethon libraries.

## External Dependencies

### APIs and Services
- **Telegram Bot API**: Primary interface for user interaction via BotFather token
- **Telegram MTProto API**: Used through Telethon for client-level operations (requires API_ID and API_HASH from my.telegram.org)

### Python Libraries
- `python-telegram-bot`: Bot framework for handling commands and messages
- `telethon`: Telegram client library for session management
- Standard library: `asyncio`, `logging`, `os`

### Required Environment Variables
Set these in the Secrets tab:
- `API_ID`: Telegram API ID (integer)
- `API_HASH`: Telegram API Hash (string)
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather