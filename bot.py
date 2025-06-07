import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telethon import TelegramClient, events
from telethon.tl.types import InputChannel
import asyncio
import re
import configparser
import time
import json
import uuid

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Telegram API credentials
API_ID = config['Telegram']['api_id']
API_HASH = config['Telegram']['api_hash']
BOT_TOKEN = config['Telegram']['bot_token']

# Ad link
AD_LINK = "https://www.profitableratecpm.com/w8b7hemg2?key=b3e4038a8d4a9224c1cf0d2d98239b3a"

# Create directories for downloads
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# User database for tracking ad visits
USER_DB_FILE = 'user_data.json'

# Initialize Telethon client
client = TelegramClient('telemedia_session', API_ID, API_HASH)

# Load or create user database
def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}}

def save_user_db(db):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(db, f)

# User database
user_db = load_user_db()

# Track total requests
if "stats" not in user_db:
    user_db["stats"] = {
        "total_requests": 0,
        "total_downloads": 0
    }
    save_user_db(user_db)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_first_name = update.effective_user.first_name
    user_id = str(update.effective_user.id)
    
    # Initialize user in database if not exists
    if user_id not in user_db["users"]:
        user_db["users"][user_id] = {
            "ad_verified": False,
            "downloads": 0,
            "last_verification": None,
            "join_date": time.time(),
            "username": update.effective_user.username or "Unknown",
            "first_name": user_first_name
        }
        save_user_db(user_db)
    
    welcome_message = (
        f"👋 *Welcome, {user_first_name}!*\n\n"
        f"I'm your Telegram Media Downloader Bot. I can help you download media from any Telegram channel or group.\n\n"
        f"🔹 Simply send me a Telegram message link containing media\n"
        f"🔹 I'll download and send it back to you\n"
        f"🔹 Works with photos, videos, and documents\n\n"
        f"Send /help to see more information."
    )
    
    # Create inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("📚 Help", callback_data="help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_message = (
        "*📚 How to use this bot:*\n\n"
        "1️⃣ Find a message with media in any Telegram channel/group\n"
        "2️⃣ Copy the message link (tap and hold on mobile, right-click on desktop)\n"
        "3️⃣ Send the link to me (format: https://t.me/channelname/123)\n"
        "4️⃣ Visit our sponsor link when prompted\n"
        "5️⃣ I'll download and send the media back to you\n\n"
        "*Supported media types:*\n"
        "🎬 Videos\n"
        "🖼️ Photos\n"
        "📄 Documents\n\n"
        "*Note:* You must be a member of private channels to download media from them."
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_message = (
        "*ℹ️ About This Bot*\n\n"
        "This Telegram Media Downloader Bot allows you to easily download media from any Telegram channel or group.\n\n"
        "🔸 *Version:* 1.0\n"
        "🔸 *Created by:* Your Name\n"
        "🔸 *Features:* Download photos, videos, and documents\n\n"
        "If you have any questions or feedback, please contact @YourUsername"
    )
    await update.message.reply_text(about_message, parse_mode='Markdown')

# Ad link with tracking
def generate_ad_link(user_id, verification_id):
    base_link = "https://www.profitableratecpm.com/w8b7hemg2?key=b3e4038a8d4a9224c1cf0d2d98239b3a"
    # Add tracking parameters to verify user visited the link
    return f"{base_link}&uid={user_id}&vid={verification_id}"

# Store verification timestamps
verification_attempts = {}

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        help_message = (
            "*📚 How to use this bot:*\n\n"
            "1️⃣ Find a message with media in any Telegram channel/group\n"
            "2️⃣ Copy the message link (tap and hold on mobile, right-click on desktop)\n"
            "3️⃣ Send the link to me (format: https://t.me/channelname/123)\n"
            "4️⃣ Visit our sponsor link when prompted\n"
            "5️⃣ I'll download and send the media back to you\n\n"
            "*Supported media types:*\n"
            "🎬 Videos\n"
            "🖼️ Photos\n"
            "📄 Documents\n\n"
            "*Note:* You must be a member of private channels to download media from them."
        )
        await query.edit_message_text(help_message, parse_mode='Markdown')
    
    elif query.data == "about":
        about_message = (
            "*ℹ️ About This Bot*\n\n"
            "This Telegram Media Downloader Bot allows you to easily download media from any Telegram channel or group.\n\n"
            "🔸 *Version:* 1.0\n"
            "🔸 *Created by:* Your Name\n"
            "🔸 *Features:* Download photos, videos, and documents\n\n"
            "If you have any questions or feedback, please contact @YourUsername"
        )
        await query.edit_message_text(about_message, parse_mode='Markdown')
    
    elif query.data.startswith("verify_"):
        # Handle ad verification
        verification_id = query.data.split("_")[1]
        user_id = str(query.from_user.id)
        
        # Check if this is the first verification attempt
        if verification_id not in verification_attempts:
            # First click - store timestamp and ask user to visit link
            verification_attempts[verification_id] = time.time()
            
            # Generate personalized ad link with tracking parameters
            personalized_ad_link = generate_ad_link(user_id, verification_id)
            
            keyboard = [
                [InlineKeyboardButton("🌐 Visit Sponsor Link", url=personalized_ad_link)],
                [InlineKeyboardButton("✅ I've Visited", callback_data=f"verify_{verification_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔒 *Verification Required*\n\n"
                "To support our free service, please visit our sponsor link before downloading.\n\n"
                "1️⃣ Click the 'Visit Sponsor Link' button\n"
                "2️⃣ Stay on the page for at least 5 seconds\n"
                "3️⃣ Return here and click 'I've Visited' again\n\n"
                "Thank you for supporting us! 🙏",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        # This is the second verification attempt, check time spent
        elapsed_time = time.time() - verification_attempts[verification_id]
        if elapsed_time < 5:  # Require at least 5 seconds on the ad page (changed from 10)
            # Not enough time spent, ask user to try again
            await query.edit_message_text(
                "⚠️ *Verification Failed*\n\n"
                f"You need to spend at least 5 seconds on the sponsor page.\n"
                f"You only spent {elapsed_time:.1f} seconds.\n\n"
                "Please try again and stay on the page longer.",
                parse_mode='Markdown'
            )
            # Remove the verification attempt so they have to start over
            del verification_attempts[verification_id]
            return
        
        # Verification successful, clean up
        del verification_attempts[verification_id]
        
        # Mark user as verified
        if user_id in user_db["users"]:
            user_db["users"][user_id]["ad_verified"] = True
            user_db["users"][user_id]["last_verification"] = time.time()
            save_user_db(user_db)
            
            # Get the pending download from context
            if "pending_downloads" in context.bot_data and verification_id in context.bot_data["pending_downloads"]:
                link = context.bot_data["pending_downloads"][verification_id]
                
                # Remove from pending downloads
                del context.bot_data["pending_downloads"][verification_id]
                
                # Process the download
                await query.edit_message_text(
                    "✅ *Thank you for supporting us!*\n\nProcessing your download now...",
                    parse_mode='Markdown'
                )
                
                # Call download function with callback query instead of update
                await process_download_from_callback(query, context, link)
            else:
                await query.edit_message_text(
                    "✅ *Verification successful!*\n\nYou can now download media. Please send a Telegram link.",
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text(
                "❌ *Verification failed.*\n\nPlease try again or contact support.",
                parse_mode='Markdown'
            )

async def extract_message_info(link):
    """Extract channel/chat ID and message ID from a Telegram link."""
    # Match patterns like https://t.me/c/1234567890/123 or https://t.me/username/123
    pattern = r'https?://t\.me/(?:c/)?([^/]+)/(\d+)'
    match = re.match(pattern, link)
    
    if match:
        channel_id = match.group(1)
        message_id = int(match.group(2))
        
        # If channel_id is numeric and starts with a number, it's a private channel
        if channel_id.isdigit():
            channel_id = int(channel_id)
        
        return channel_id, message_id
    return None, None

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle media download requests."""
    link = update.message.text
    user_id = str(update.effective_user.id)
    
    if not link.startswith('https://t.me/'):
        await update.message.reply_text('❌ *Please send a valid Telegram link.*', parse_mode='Markdown')
        return
    
    # Check if user is in database
    if user_id not in user_db["users"]:
        user_db["users"][user_id] = {
            "ad_verified": False,
            "downloads": 0,
            "last_verification": None
        }
        save_user_db(user_db)
    
    # Check if user needs to verify (every 3 downloads or if never verified)
    user_data = user_db["users"][user_id]
    needs_verification = (
        not user_data["ad_verified"] or 
        user_data["downloads"] % 3 == 0 or
        (user_data["last_verification"] and time.time() - user_data["last_verification"] > 86400)  # 24 hours
    )
    
    if needs_verification:
        # Generate verification ID
        verification_id = str(uuid.uuid4())
        
        # Store pending download
        if "pending_downloads" not in context.bot_data:
            context.bot_data["pending_downloads"] = {}
        context.bot_data["pending_downloads"][verification_id] = link
        
        # Generate personalized ad link with tracking parameters
        personalized_ad_link = generate_ad_link(user_id, verification_id)
        
        # Create verification message with ad link
        keyboard = [
            [InlineKeyboardButton("🌐 Visit Sponsor Link", url=personalized_ad_link)],
            [InlineKeyboardButton("✅ I've Visited", callback_data=f"verify_{verification_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔒 *Verification Required*\n\n"
            "To support our free service, please visit our sponsor link before downloading.\n\n"
            "1️⃣ Click the 'Visit Sponsor Link' button\n"
            "2️⃣ Stay on the page for at least 10 seconds\n"
            "3️⃣ Return here and click 'I've Visited'\n\n"
            "Thank you for supporting us! 🙏",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    # If user is verified, process the download
    await process_download(update, context, link)
    
    # Update download count
    user_db["users"][user_id]["downloads"] += 1
    save_user_db(user_db)

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, link: str) -> None:
    """Process the actual download after verification."""
    # Send a styled processing message
    processing_message = await update.message.reply_text(
        '🔍 *Processing your request...*', 
        parse_mode='Markdown'
    )
    
    channel_id, message_id = await extract_message_info(link)
    
    if not channel_id or not message_id:
        await processing_message.edit_text(
            '❌ *Invalid link format. Please send a valid Telegram message link.*', 
            parse_mode='Markdown'
        )
        return
    
    try:
        # Connect to Telegram
        if not client.is_connected():
            await client.connect()
            
        if await client.is_user_authorized():
            # Get the message
            message = await client.get_messages(channel_id, ids=message_id)
            
            if message and message.media:
                # Download the media with progress updates
                await processing_message.edit_text('⬇️ *Downloading media...*', parse_mode='Markdown')
                start_time = time.time()
                file_path = await client.download_media(message, 'downloads/')
                download_time = time.time() - start_time
                
                # Send the downloaded media back to the user
                await processing_message.edit_text(
                    f'✅ *Download complete!*\n⏱️ Time: {download_time:.1f}s\n📤 *Sending media to you...*', 
                    parse_mode='Markdown'
                )
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    caption = f"📁 *{file_name}*\n📊 Size: {file_size:.1f} MB"
                    
                    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        await update.message.reply_video(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await update.message.reply_photo(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_document(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    
                    # Clean up
                    os.remove(file_path)
                    await processing_message.delete()
                else:
                    await processing_message.edit_text('❌ *Failed to download media.*', parse_mode='Markdown')
            else:
                await processing_message.edit_text('❌ *No media found in the message.*', parse_mode='Markdown')
        else:
            await processing_message.edit_text(
                '🔐 *Bot is not authorized. Please run the auth.py script first.*', 
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        await processing_message.edit_text(
            f'❌ *Error:* {str(e)}', 
            parse_mode='Markdown'
        )

async def process_download_from_callback(query, context: ContextTypes.DEFAULT_TYPE, link: str) -> None:
    """Process download from a callback query."""
    # Use the message from the callback query
    message = query.message
    
    # Edit the current message instead of creating a new one
    await query.edit_message_text(
        '🔍 *Processing your request...*', 
        parse_mode='Markdown'
    )
    
    channel_id, message_id = await extract_message_info(link)
    
    if not channel_id or not message_id:
        await query.edit_message_text(
            '❌ *Invalid link format. Please send a valid Telegram message link.*', 
            parse_mode='Markdown'
        )
        return
    
    try:
        # Connect to Telegram
        if not client.is_connected():
            await client.connect()
            
        if await client.is_user_authorized():
            # Get the message
            telegram_message = await client.get_messages(channel_id, ids=message_id)
            
            if telegram_message and telegram_message.media:
                # Download the media with progress updates
                await query.edit_message_text('⬇️ *Downloading media...*', parse_mode='Markdown')
                start_time = time.time()
                file_path = await client.download_media(telegram_message, 'downloads/')
                download_time = time.time() - start_time
                
                # Send the downloaded media back to the user
                await query.edit_message_text(
                    f'✅ *Download complete!*\n⏱️ Time: {download_time:.1f}s\n📤 *Sending media to you...*', 
                    parse_mode='Markdown'
                )
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    caption = f"📁 *{file_name}*\n📊 Size: {file_size:.1f} MB"
                    
                    chat_id = query.message.chat_id
                    
                    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        await context.bot.send_video(
                            chat_id=chat_id,
                            video=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        await context.bot.send_document(
                            chat_id=chat_id,
                            document=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    
                    # Clean up
                    os.remove(file_path)
                    await query.edit_message_text("✅ *Media sent successfully!*", parse_mode='Markdown')
                else:
                    await query.edit_message_text('❌ *Failed to download media.*', parse_mode='Markdown')
            else:
                await query.edit_message_text('❌ *No media found in the message.*', parse_mode='Markdown')
        else:
            await query.edit_message_text(
                '🔐 *Bot is not authorized. Please run the auth.py script first.*', 
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        await query.edit_message_text(
            f'❌ *Error:* {str(e)}', 
            parse_mode='Markdown'
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send bot statistics to admin."""
    user_id = str(update.effective_user.id)
    
    # Only allow the admin to access this command
    if user_id != "5951639932":
        await update.message.reply_text("⛔ *This command is only available to administrators.*", parse_mode='Markdown')
        return
    
    # Calculate statistics
    total_users = len(user_db["users"])
    total_requests = user_db["stats"]["total_requests"]
    total_downloads = user_db["stats"]["total_downloads"]
    
    # Get most recent users (up to 5)
    recent_users = []
    for uid, data in sorted(user_db["users"].items(), key=lambda x: x[1].get("join_date", 0), reverse=True)[:5]:
        username = data.get("username", "Unknown")
        first_name = data.get("first_name", "Unknown")
        join_date = data.get("join_date", 0)
        join_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(join_date)) if join_date else "Unknown"
        recent_users.append(f"• {first_name} (@{username}) - {join_date_str}")
    
    # Get most active users (up to 5)
    active_users = []
    for uid, data in sorted(user_db["users"].items(), key=lambda x: x[1].get("downloads", 0), reverse=True)[:5]:
        username = data.get("username", "Unknown")
        first_name = data.get("first_name", "Unknown")
        downloads = data.get("downloads", 0)
        active_users.append(f"• {first_name} (@{username}) - {downloads} downloads")
    
    # Format the status message
    status_message = (
        "📊 *Bot Statistics*\n\n"
        f"👥 *Total Users:* {total_users}\n"
        f"🔢 *Total Requests:* {total_requests}\n"
        f"⬇️ *Total Downloads:* {total_downloads}\n\n"
        f"🆕 *Recent Users:*\n"
        f"{chr(10).join(recent_users)}\n\n"
        f"🏆 *Most Active Users:*\n"
        f"{chr(10).join(active_users)}"
    )
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle media download requests."""
    link = update.message.text
    user_id = str(update.effective_user.id)
    
    # Update total requests counter
    user_db["stats"]["total_requests"] += 1
    save_user_db(user_db)
    
    if not link.startswith('https://t.me/'):
        await update.message.reply_text('❌ *Please send a valid Telegram link.*', parse_mode='Markdown')
        return
    
    # Check if user is in database
    if user_id not in user_db["users"]:
        user_db["users"][user_id] = {
            "ad_verified": False,
            "downloads": 0,
            "last_verification": None
        }
        save_user_db(user_db)
    
    # Check if user needs to verify (every 3 downloads or if never verified)
    user_data = user_db["users"][user_id]
    needs_verification = (
        not user_data["ad_verified"] or 
        user_data["downloads"] % 3 == 0 or
        (user_data["last_verification"] and time.time() - user_data["last_verification"] > 86400)  # 24 hours
    )
    
    if needs_verification:
        # Generate verification ID
        verification_id = str(uuid.uuid4())
        
        # Store pending download
        if "pending_downloads" not in context.bot_data:
            context.bot_data["pending_downloads"] = {}
        context.bot_data["pending_downloads"][verification_id] = link
        
        # Generate personalized ad link with tracking parameters
        personalized_ad_link = generate_ad_link(user_id, verification_id)
        
        # Create verification message with ad link
        keyboard = [
            [InlineKeyboardButton("🌐 Visit Sponsor Link", url=personalized_ad_link)],
            [InlineKeyboardButton("✅ I've Visited", callback_data=f"verify_{verification_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔒 *Verification Required*\n\n"
            "To support our free service, please visit our sponsor link before downloading.\n\n"
            "1️⃣ Click the 'Visit Sponsor Link' button\n"
            "2️⃣ Stay on the page for at least 10 seconds\n"
            "3️⃣ Return here and click 'I've Visited'\n\n"
            "Thank you for supporting us! 🙏",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    # If user is verified, process the download
    await process_download(update, context, link)
    
    # Update download count
    user_db["users"][user_id]["downloads"] += 1
    save_user_db(user_db)

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, link: str) -> None:
    """Process the actual download after verification."""
    # Send a styled processing message
    processing_message = await update.message.reply_text(
        '🔍 *Processing your request...*', 
        parse_mode='Markdown'
    )
    
    channel_id, message_id = await extract_message_info(link)
    
    if not channel_id or not message_id:
        await processing_message.edit_text(
            '❌ *Invalid link format. Please send a valid Telegram message link.*', 
            parse_mode='Markdown'
        )
        return
    
    try:
        # Connect to Telegram
        if not client.is_connected():
            await client.connect()
            
        if await client.is_user_authorized():
            # Get the message
            message = await client.get_messages(channel_id, ids=message_id)
            
            if message and message.media:
                # Download the media with progress updates
                await processing_message.edit_text('⬇️ *Downloading media...*', parse_mode='Markdown')
                start_time = time.time()
                file_path = await client.download_media(message, 'downloads/')
                download_time = time.time() - start_time
                
                # Send the downloaded media back to the user
                await processing_message.edit_text(
                    f'✅ *Download complete!*\n⏱️ Time: {download_time:.1f}s\n📤 *Sending media to you...*', 
                    parse_mode='Markdown'
                )
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    caption = f"📁 *{file_name}*\n📊 Size: {file_size:.1f} MB"
                    
                    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        await update.message.reply_video(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await update.message.reply_photo(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_document(
                            open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    
                    # Clean up
                    os.remove(file_path)
                    await processing_message.delete()
                else:
                    await processing_message.edit_text('❌ *Failed to download media.*', parse_mode='Markdown')
            else:
                await processing_message.edit_text('❌ *No media found in the message.*', parse_mode='Markdown')
        else:
            await processing_message.edit_text(
                '🔐 *Bot is not authorized. Please run the auth.py script first.*', 
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        await processing_message.edit_text(
            f'❌ *Error:* {str(e)}', 
            parse_mode='Markdown'
        )

async def process_download_from_callback(query, context: ContextTypes.DEFAULT_TYPE, link: str) -> None:
    """Process download from a callback query."""
    # Use the message from the callback query
    message = query.message
    
    # Edit the current message instead of creating a new one
    await query.edit_message_text(
        '🔍 *Processing your request...*', 
        parse_mode='Markdown'
    )
    
    channel_id, message_id = await extract_message_info(link)
    
    if not channel_id or not message_id:
        await query.edit_message_text(
            '❌ *Invalid link format. Please send a valid Telegram message link.*', 
            parse_mode='Markdown'
        )
        return
    
    try:
        # Connect to Telegram
        if not client.is_connected():
            await client.connect()
            
        if await client.is_user_authorized():
            # Get the message
            telegram_message = await client.get_messages(channel_id, ids=message_id)
            
            if telegram_message and telegram_message.media:
                # Download the media with progress updates
                await query.edit_message_text('⬇️ *Downloading media...*', parse_mode='Markdown')
                start_time = time.time()
                file_path = await client.download_media(telegram_message, 'downloads/')
                download_time = time.time() - start_time
                
                # Send the downloaded media back to the user
                await query.edit_message_text(
                    f'✅ *Download complete!*\n⏱️ Time: {download_time:.1f}s\n📤 *Sending media to you...*', 
                    parse_mode='Markdown'
                )
                
                if file_path:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    caption = f"📁 *{file_name}*\n📊 Size: {file_size:.1f} MB"
                    
                    chat_id = query.message.chat_id
                    
                    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        await context.bot.send_video(
                            chat_id=chat_id,
                            video=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await context.bot.send_photo(
                            chat_id=chat_id,
                            photo=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        await context.bot.send_document(
                            chat_id=chat_id,
                            document=open(file_path, 'rb'), 
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    
                    # Clean up
                    os.remove(file_path)
                    await query.edit_message_text("✅ *Media sent successfully!*", parse_mode='Markdown')
                else:
                    await query.edit_message_text('❌ *Failed to download media.*', parse_mode='Markdown')
            else:
                await query.edit_message_text('❌ *No media found in the message.*', parse_mode='Markdown')
        else:
            await query.edit_message_text(
                '🔐 *Bot is not authorized. Please run the auth.py script first.*', 
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        await query.edit_message_text(
            f'❌ *Error:* {str(e)}', 
            parse_mode='Markdown'
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("status", status_command))  # Add status command
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()