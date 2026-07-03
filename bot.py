import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from dotenv import load_dotenv
from ip_lookup import validate_ip, fetch_ip_details, format_ip_data

# Load configurations
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Setup Logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# State machine values
WAITING_FOR_IP = 1

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🌍 Lookup IP Address", callback_data="btn_lookup_prompt")],
        [InlineKeyboardButton("📍 My IP Information", callback_data="btn_my_ip")],
        [
            InlineKeyboardButton("📚 IP Guide", callback_data="btn_guide"),
            InlineKeyboardButton("❓ Help", callback_data="btn_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends structured professional text profile to start interface workflows."""
    welcome_msg = (
        "👋 **Welcome to IPLookup Bot!**\n\n"
        "Instantly retrieve detailed information about any public IP address.\n\n"
        "🌍 Lookup any IP address\n"
        "📍 View your own IP details\n"
        "🛰️ Discover location, ISP, timezone, ASN, and more\n"
        "⚡ Fast, accurate, and easy to use\n\n"
        "Select an option below to get started."
    )
    if update.message:
        await update.message.reply_text(welcome_msg, parse_mode="Markdown", reply_markup=get_main_menu())
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_msg, parse_mode="Markdown", reply_markup=get_main_menu())
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Outputs basic assistance documentation strings."""
    help_text = (
        "❓ **IPLookup Bot Assistance Manual**\n\n"
        "• **/start** - Display standard runtime dashboard options.\n"
        "• **/help** - Display this diagnostic manual.\n\n"
        "💡 **Operational Insights:**\n"
        "Click on **Lookup IP Address**, then send any valid external IP string like `8.8.8.8` or `2001:4860:4860::8888`."
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="Markdown")
    elif update.callback_query:
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_home")]]
        await update.callback_query.edit_message_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides high level educational framework on IP architectures."""
    guide_text = (
        "📚 **IP Address Knowledge Guide**\n\n"
        "🔹 **What is an IP Address?**\n"
        "An IP (Internet Protocol) address is a unique identifier assigned to devices connected to a network, serving as a digital home address for data routing.\n\n"
        "🔹 **IPv4 vs IPv6**\n"
        "• **IPv4:** Expressed as a 32-bit numeric value (`192.168.1.1`). It yields roughly 4.3 billion configurations, which the world has now exhausted.\n"
        "• **IPv6:** Expressed as a 128-bit hexadecimal value (`2001:0db8:85a3::8a2e:0370:7334`). Built to ensure infinite addressing capacity for the future.\n\n"
        "🔹 **Public vs Private**\n"
        "Public IPs can be searched globally across internet pathways. Private IPs are hidden behind routers on localized intranets (like home Wi-Fi networks) and cannot be tracked by this tool."
    )
    if update.message:
        await update.message.reply_text(guide_text, parse_mode="Markdown")
    elif update.callback_query:
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu_home")]]
        await update.callback_query.edit_message_text(guide_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def prompt_ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Transitions workflow context to wait for an IP input string."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌍 **IP Target Lookup Engine**\n\n"
        "Please type or paste the public **IPv4** or **IPv6** address you want to inspect below:",
        parse_mode="Markdown"
    )
    return WAITING_FOR_IP

async def execute_ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validates raw text from user and runs lookup logic pipelines."""
    ip_str = update.message.text.strip()
    
    if not validate_ip(ip_str):
        await update.message.reply_text(
            "❌ **Invalid Public IP Address**\n\n"
            "Please check for typos. The address must be a valid public global address (Private networks like `192.168.x.x` or `10.x.x.x` are not supported).\n\n"
            "Try again or type /start to cancel:",
            parse_mode="Markdown"
        )
        return WAITING_FOR_IP

    status_msg = await update.message.reply_text("🔍 *Querying geolocation registries...*", parse_mode="Markdown")
    
    result = await fetch_ip_details(ip_str)
    await status_msg.delete()

    if "error" in result:
        await update.message.reply_text(f"❌ Failed to fetch telemetry data: `{result['error']}`", parse_mode="Markdown")
    else:
        formatted_report = format_ip_data(result)
        keyboard = [
            [InlineKeyboardButton("🌍 Lookup Another", callback_data="btn_lookup_prompt")],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="menu_home")]
        ]
        await update.message.reply_text(formatted_report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    return ConversationHandler.END

async def handle_my_ip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches the IP profile of the bot server framework itself as fallback query context."""
    query = update.callback_query
    await query.answer()
    
    result = await fetch_ip_details("")
    
    if "error" in result:
        await query.edit_message_text(f"❌ Failed to resolve your server profile: `{result['error']}`")
        return

    formatted_report = (
        "📍 **Your Connection Context Profile**\n"
        "_(Note: This represents the current public entry point matching server requests)_\n\n"
    ) + format_ip_data(result)
    
    keyboard = [[InlineKeyboardButton("⬅️ Main Menu", callback_data="menu_home")]]
    await query.edit_message_text(formatted_report, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def main_async():
    """Asynchronous orchestrator initializing the framework cleanly under Python 3.14+."""
    if not BOT_TOKEN:
        logger.error("System crash avoided: Environment Variable 'BOT_TOKEN' is missing.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Define robust input loop using ConversationHandler
    lookup_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(prompt_ip_lookup, pattern="^btn_lookup_prompt$")],
        states={
            WAITING_FOR_IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, execute_ip_lookup)]
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=True
    )

    # Attach command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Attach dynamic execution handlers
    application.add_handler(lookup_conv)
    application.add_handler(CallbackQueryHandler(start, pattern="^menu_home$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^btn_help$"))
    application.add_handler(CallbackQueryHandler(guide_command, pattern="^btn_guide$"))
    application.add_handler(CallbackQueryHandler(handle_my_ip, pattern="^btn_my_ip$"))

    logger.info("IPLookup Bot engine initialized cleanly. Active long-polling initiated...")
    
    # Explicitly manage modern async loop startup sequence
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    """Synchronous framework initialisation wrapping modern async runtimes."""
    try:
        asyncio.run(main_async())
    except Exception as e:
        logger.critical(f"Bot execution loop crashed: {e}")

if __name__ == "__main__":
    main()
