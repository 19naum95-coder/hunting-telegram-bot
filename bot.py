import logging
import json
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
OWNER_ID = int(os.getenv('OWNER_ID', '5060558519'))

# Словарь животных с шансами и наградами
ANIMALS = {
    'заяц': {'chance': 25, 'xp': 10, 'silver': 50},
    'лиса': {'chance': 20, 'xp': 15, 'silver': 75},
    'олень': {'chance': 15, 'xp': 25, 'silver': 120},
    'кабан': {'chance': 12, 'xp': 30, 'silver': 150},
    'волк': {'chance': 10, 'xp': 40, 'silver': 200},
    'медведь': {'chance': 8, 'xp': 60, 'silver': 350},
    'орел': {'chance': 6, 'xp': 45, 'silver': 250},
    'лев': {'chance': 4, 'xp': 80, 'silver': 500},
    'тигр': {'chance': 3, 'xp': 90, 'silver': 600},
    'носорог': {'chance': 2, 'xp': 100, 'silver': 750},
    'слон': {'chance': 2, 'xp': 110, 'silver': 800},
    'единорог': {'chance': 1, 'xp': 200, 'silver': 1500},
    'дракон': {'chance': 0.5, 'xp': 300, 'silver': 2500},
    'феникс': {'chance': 0.3, 'xp': 500, 'silver': 5000},
}

# Стикеры животных
ANIMAL_STICKERS = {
    'заяц': 'CAACAgIAAxkBAAERIAhp7wO4wOPZ1WkRB5ZauAY1G9nIhQACJKgAAgmceEs5o8d6vvjpaDsE',
    'лиса': 'CAACAgIAAxkBAAERIAxp7wRQD5dgu5pIGv4FAAFgAaWzz2YAAtyfAAI6MXhLGIpNwyq_7EY7BA',
    'олень': 'CAACAgIAAxkBAAERIA5p7wRqGuZUEko40JNGmuaY_1MU-AAC5I8AApOTeUsM1n-vTuBJQTsE',
    'кабан': 'CAACAgIAAxkBAAERIBBp7wR-omhtvYyBncipNIyQhP81BQACDJYAAkhSeEvO3xLJrTTdLjsE',
    'волк': 'CAACAgIAAxkBAAERIBJp7wSXTc_pKKR3txsJ81pIeC2_bQACjYwAAouYeUs4bDvB8cj2FjsE',
    'медведь': 'CAACAgIAAxkBAAERIBRp7wS3UchaGE1e0sy0gV0K5V7tiwACCacAAoFdeEtSkwj0d_vrBzsE',
    'орел': 'CAACAgIAAxkBAAERIBZp7wTSsXSl0ZO_XAivtUU_QXWR6gAC0ZUAAuwWeUtnVY2z-2MIczsE',
    'лев': 'CAACAgIAAxkBAAERIBhp7wUgXaobat3tqC8Z2qc3oWzmqQACN6AAAkuveUtfbNZ8ePSisTsE',
    'тигр': 'CAACAgIAAxkBAAERIBpp7wUzoONBYhpyZBT-uoTDi-VY1AACRZsAAkMIeUum0Y7VOk9k4TsE',
    'носорог': 'CAACAgIAAxkBAAERIBxp7wVHvDVp7lu-eDBBp-OwvBj8IwACrJ8AAsCreEsY1KhJ2wsBWjsE',
    'слон': 'CAACAgIAAxkBAAERIB5p7wVc64nGDOaDBJZEaulbgIXuDQACXp8AAvGqeUvLKvWSc1VTTDsE',
    'единорог': 'CAACAgIAAxkBAAERICBp7wVuSQABA3jxJjirpEvAr9wCGKoAAn-WAAJnpnhLd0ftlOHGtLM7BA',
    'дракон': 'CAACAgIAAxkBAAERICJp7wWCjKIvMbq_7w3_4yUbBi_oXwACypwAAgwIeEtbnfEUoTnsGDsE',
    'феникс': 'CAACAgIAAxkBAAERICRp7wW0AY8HQZq5X7FNZl5e-YXhuAACVZcAAtkFeUvnQOcZEzV2-TsE',
}

# Функции для работы с данными пользователей
def load_users_data():
    try:
        with open('users_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users_data(data):
    with open('users_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    users_data = load_users_data()
    user_id = str(user_id)
    
    if user_id not in users_data:
        users_data[user_id] = {
            'username': '',
            'first_name': '',
            'registered': datetime.now().strftime('%Y-%m-%d'),
            'last_active': datetime.now().isoformat(),
            'level': 1,
            'xp': 0,
            'silver': 100,
            'inventory': {},
            'total_hunts': 0,
            'successful_hunts': 0
        }
        save_users_data(users_data)
    
    return users_data[user_id]

def update_user_data(user_id, data):
    users_data = load_users_data()
    user_id = str(user_id)
    users_data[user_id] = data
    users_data[user_id]['last_active'] = datetime.now().isoformat()
    save_users_data(users_data)

def calculate_level(xp):
    return int((xp / 100) ** 0.5) + 1

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Обновляем информацию о пользователе
    user_data['username'] = update.effective_user.username or 'Аноним'
    user_data['first_name'] = update.effective_user.first_name or 'Игрок'
    update_user_data(user_id, user_data)
    
    users_count = len(load_users_data())
    
    await update.message.reply_text(
        f"🎯 Добро пожаловать, {update.effective_user.first_name}!\n\n"
        f"🏹 Бот охоты и рыбалки\n"
        f"👥 Игроков: {users_count}\n\n"
        f"Команды:\n"
        f"/hunt - Охота\n"
        f"/stats - Статистика\n"
        f"/me - Профиль\n"
        f"/help - Помощь"
    )

# Команда /hunt
async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Увеличиваем счётчик охот
    user_data['total_hunts'] += 1
    
    # Выбираем случайное животное с учётом шансов
    animals_list = []
    for animal, data in ANIMALS.items():
        animals_list.extend([animal] * int(data['chance'] * 10))
    
    animal = random.choice(animals_list)
    animal_data = ANIMALS[animal]
    
    # Проверяем попадание (70% шанс)
    if random.random() < 0.7:
        # Попадание!
        user_data['successful_hunts'] += 1
        user_data['xp'] += animal_data['xp']
        user_data['silver'] += animal_data['silver']
        
        # Добавляем в инвентарь
        if animal not in user_data['inventory']:
            user_data['inventory'][animal] = 0
        user_data['inventory'][animal] += 1
        
        # Пересчитываем уровень
        old_level = user_data['level']
        user_data['level'] = calculate_level(user_data['xp'])
        
        update_user_data(user_id, user_data)
        
        # Отправляем стикер
        sticker_id = ANIMAL_STICKERS.get(animal)
        if sticker_id:
            try:
                await update.message.reply_sticker(sticker=sticker_id)
            except:
                pass
        
        # Сообщение о результате
        message = (
            f"🎯 ПОПАДАНИЕ!\n\n"
            f"Вы подстрелили: {animal.title()}\n"
            f"💰 +{animal_data['silver']} серебра\n"
            f"⭐ +{animal_data['xp']} опыта\n"
        )
        
        if user_data['level'] > old_level:
            message += f"\n🎉 НОВЫЙ УРОВЕНЬ: {user_data['level']}!"
        
    else:
        # Промах
        update_user_data(user_id, user_data)
        message = f"❌ ПРОМАХ!\n\n{animal.title()} убежал..."
    
    await update.message.reply_text(message)

# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_data = load_users_data()
    
    if user_id == OWNER_ID:
        # Админ-статистика
        total = len(users_data)
        now = datetime.now()
        active_24h = 0
        new_today = 0
        new_week = 0
        
        for uid, data in users_data.items():
            try:
                last = datetime.fromisoformat(data['last_active'])
                if now - last < timedelta(hours=24):
                    active_24h += 1
                
                registered = datetime.strptime(data['registered'], '%Y-%m-%d')
                if (now - registered).days == 0:
                    new_today += 1
                if (now - registered).days <= 7:
                    new_week += 1
            except:
                pass
        
        total_hunts = sum(u.get('total_hunts', 0) for u in users_data.values())
        total_silver = sum(u.get('silver', 0) for u in users_data.values())
        
        message = (
            f"👑 АДМИН-СТАТИСТИКА\n\n"
            f"👥 Всего пользователей: {total}\n"
            f"🟢 Активных за 24ч: {active_24h}\n"
            f"📈 Новых за сегодня: {new_today}\n"
            f"📅 Новых за неделю: {new_week}\n\n"
            f"📊 ОБЩАЯ СТАТИСТИКА:\n"
            f"🏹 Всего охот: {total_hunts}\n"
            f"💰 Серебра в игре: {total_silver}\n"
        )
    else:
        # Обычная статистика
        total = len(users_data)
        total_hunts = sum(u.get('total_hunts', 0) for u in users_data.values())
        
        message = (
            f"📊 СТАТИСТИКА БОТА\n\n"
            f"👥 Игроков в боте: {total}\n"
            f"🏹 Всего охот: {total_hunts}\n"
        )
    
    await update.message.reply_text(message)

# Команда /me
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    accuracy = (user_data['successful_hunts'] / user_data['total_hunts'] * 100) if user_data['total_hunts'] > 0 else 0
    
    inventory_text = ""
    if user_data['inventory']:
        for animal, count in sorted(user_data['inventory'].items(), key=lambda x: x[1], reverse=True)[:5]:
            inventory_text += f"{animal.title()}: {count} шт.\n"
    else:
        inventory_text = "Пусто"
    
    message = (
        f"👤 {user_data['first_name']}\n"
        f"@{user_data['username']}\n\n"
        f"📊 СТАТИСТИКА:\n"
        f"Уровень: {user_data['level']}\n"
        f"Опыт: {user_data['xp']} XP\n"
        f"💰 Серебро: {user_data['silver']}\n\n"
        f"🏹 ОХОТА:\n"
        f"Всего охот: {user_data['total_hunts']}\n"
        f"Успешных: {user_data['successful_hunts']}\n"
        f"Точность: {accuracy:.1f}%\n\n"
        f"🎒 ИНВЕНТАРЬ (топ-5):\n{inventory_text}"
    )
    
    await update.message.reply_text(message)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "📖 ПОМОЩЬ\n\n"
        "🎯 Основные команды:\n"
        "/hunt - Охота на животных\n"
        "/stats - Статистика бота\n"
        "/me - Ваш профиль\n\n"
        "🏹 Как играть:\n"
        "1. Используйте /hunt для охоты\n"
        "2. Получайте опыт и серебро\n"
        "3. Повышайте уровень\n"
        "4. Собирайте коллекцию животных\n\n"
        "🎲 Шанс попадания: 70%\n"
        "⭐ Редкие животные дают больше наград!"
    )
    
    await update.message.reply_text(message)

# Команда /admin (только для владельца)
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Топ игроков", callback_data="admin_top")],
    ]
    
    await update.message.reply_text(
        "👑 АДМИН-ПАНЕЛЬ\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработчик callback кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_stats":
        users_data = load_users_data()
        total = len(users_data)
        total_hunts = sum(u.get('total_hunts', 0) for u in users_data.values())
        total_silver = sum(u.get('silver', 0) for u in users_data.values())
        
        message = (
            f"📊 ПОДРОБНАЯ СТАТИСТИКА\n\n"
            f"👥 Пользователей: {total}\n"
            f"🏹 Охот: {total_hunts}\n"
            f"💰 Серебра: {total_silver}\n"
        )
        
        await query.edit_message_text(message)
    
    elif query.data == "admin_top":
        users_data = load_users_data()
        
        # Сортируем по уровню
        top_users = sorted(
            [(uid, data) for uid, data in users_data.items()],
            key=lambda x: x[1].get('level', 0),
            reverse=True
        )[:10]
        
        message = "🏆 ТОП-10 ИГРОКОВ:\n\n"
        for i, (uid, data) in enumerate(top_users, 1):
            username = data.get('first_name', 'Игрок')
            level = data.get('level', 1)
            message += f"{i}. {username} - Ур.{level}\n"
        
        await query.edit_message_text(message)

# Главная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hunt", hunt))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("me", me))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
