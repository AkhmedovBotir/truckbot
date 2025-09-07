import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

from config import BOT_TOKEN, ADMIN_IDS
from database import db
from handlers import handlers, WAITING_NAME, WAITING_PHONE, WAITING_TRACK_PHONE, WAITING_TRACK_CODE, WAITING_CHANNEL
from scheduler import scheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Registration conversation handler
    registration_conv = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_name)],
            WAITING_PHONE: [
                MessageHandler(filters.CONTACT, handlers.handle_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_phone)
            ],
        },
        fallbacks=[CommandHandler('start', handlers.start)],
    )

    # Track code assignment conversation handler
    track_code_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📦 Trek kod$'), handlers.track_code_menu)],
        states={
            WAITING_TRACK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_track_phone)],
            WAITING_TRACK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_track_code)],
        },
        fallbacks=[MessageHandler(filters.Regex('^❌ Bekor qilish$'), handlers.start)],
    )

    # Channels management conversation handler
    channels_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📢 Kanallar$'), handlers.channels_management)],
        states={
            WAITING_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_channel_input)],
        },
        fallbacks=[MessageHandler(filters.Regex('^❌ Bekor qilish$'), handlers.start)],
    )



    # Add handlers
    application.add_handler(registration_conv)
    application.add_handler(track_code_conv)
    application.add_handler(channels_conv)
    
    # Command handlers
    application.add_handler(CommandHandler('start', handlers.start))
    
    # Message handlers for menu buttons
    application.add_handler(MessageHandler(filters.Regex('^🔍 Trek kodini tekshirish$'), handlers.check_track_code))
    application.add_handler(MessageHandler(filters.Regex('^👤 Mening profilim$'), handlers.my_profile))
    
    # Admin handlers
    application.add_handler(MessageHandler(filters.Regex('^💱 Valyuta konverteri$'), handlers.currency_converter))
    application.add_handler(MessageHandler(filters.Regex('^👥 Foydalanuvchilar$'), handlers.users_list))
    application.add_handler(MessageHandler(filters.Regex('^📊 Statistika$'), handlers.statistics))
    application.add_handler(MessageHandler(filters.Regex('^📤 Eksport$'), handlers.export_users))
    
    # Text message handler (must be last to avoid conflicts)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text_message))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handlers.handle_callback))
    
    # Error handler
    application.add_error_handler(error_handler)

    # Initialize database and scheduler
    async def post_init(application):
        await db.init_db()
        await scheduler.update_schedule()
        scheduler.start()
        print("Bot muvaffaqiyatli ishga tushirildi!")

    # Set post init
    application.post_init = post_init

    # Run the bot
    print("Bot ishga tushirilmoqda...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()