import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Привет! Я бот для управления охотой!\n\n"
        "Доступные команды:\n"
        "/start - Начать\n"
        "/help - Помощь\n"
        "/hunt - Начать охоту"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Помощь:\n\n"
        "/start - Запустить бота\n"
        "/help - Показать эту помощь\n"
        "/hunt - Начать охоту"
    )

async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏹 Охота началась!\n"
        "Удачи в поисках добычи! 🦌"
    )

def main():
    logger.info("🚀 Запуск бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hunt", hunt))
    
    logger.info("✅ Бот запущен и ожидает сообщений!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
