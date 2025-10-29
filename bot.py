import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Импортируем наши модули
from config import BOT_TOKEN, ZODIAC_EMOJIS
from database import init_database, get_zodiac_sign, save_user_data, get_user_data
from horoscope_parser import horoscope_parser

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    welcome_text = f"""
Привет, {user.first_name}! 👋 Я твой персональный астробот! 🌟

Я могу:
📅 Сохранить твою дату рождения
♈ Определить твой знак зодиака  
🔮 Показать актуальный гороскоп на сегодня

Используй команды:
/setbirth - Указать дату рождения
/myhoroscope - Получить гороскоп на сегодня
/mysign - Узнать свой знак зодиака
/update - Обновить гороскоп (если устарел)
    """
    
    # Создаем клавиатуру с командами
    keyboard = [
        ['/setbirth', '/myhoroscope'],
        ['/mysign', '/update']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Команда для установки даты рождения
async def set_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Введи свою дату рождения в формате ДД.ММ.ГГГГ\n"
        "Например: 15.09.1990"
    )

# Обработка ввода даты рождения
async def handle_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    
    try:
        # Парсим дату
        day, month, year = map(int, text.split('.'))
        birth_date = f"{day:02d}.{month:02d}.{year}"
        
        # Проверяем валидность даты
        datetime.strptime(birth_date, '%d.%m.%Y')
        
        # Определяем знак зодиака
        zodiac_sign = get_zodiac_sign(day, month)
        emoji = ZODIAC_EMOJIS.get(zodiac_sign, '✨')
        
        # Сохраняем в базу данных
        save_user_data(user.id, user.username, birth_date, zodiac_sign)
        
        response = (
            f"✅ Отлично! Я сохранил твою дату рождения: {birth_date}\n\n"
            f"{emoji} Твой знак зодиака: {zodiac_sign.capitalize()} {emoji}\n\n"
            f"Теперь используй /myhoroscope чтобы получить гороскоп на сегодня!"
        )
        
    except ValueError:
        response = "❌ Неправильный формат даты! Пожалуйста, введи дату в формате ДД.ММ.ГГГГ\nНапример: 15.09.1990"
    except Exception as e:
        response = "❌ Произошла ошибка. Попробуй еще раз!"
        logging.error(f"Error saving birth date: {e}")
    
    await update.message.reply_text(response)

# Команда для получения знака зодиака
async def get_my_sign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    user_data = get_user_data(user.id)
    
    if user_data:
        zodiac_sign = user_data['zodiac_sign']
        birth_date = user_data['birth_date']
        emoji = ZODIAC_EMOJIS.get(zodiac_sign, '✨')
        
        response = (
            f"{emoji} Твой знак зодиака: {zodiac_sign.capitalize()} {emoji}\n"
            f"📅 Дата рождения: {birth_date}\n\n"
            f"Хочешь гороскоп на сегодня? Используй /myhoroscope"
        )
    else:
        response = (
            "❌ Я еще не знаю твою дату рождения.\n"
            "Используй /setbirth чтобы указать ее!"
        )
    
    await update.message.reply_text(response)

# Команда для получения гороскопа
async def get_my_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # Показываем статус "печатает"
    await update.message.reply_chat_action(action='typing')
    
    user_data = get_user_data(user.id)
    
    if user_data:
        zodiac_sign = user_data['zodiac_sign']
        emoji = ZODIAC_EMOJIS.get(zodiac_sign, '✨')
        
        # Получаем гороскоп из парсера
        horoscope = await horoscope_parser.get_daily_horoscope(zodiac_sign)
        
        response = (
            f"🔮 Гороскоп на сегодня для {zodiac_sign.capitalize()} {emoji}\n\n"
            f"{horoscope}\n\n"
            f"💫 Актуально на: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
    else:
        response = (
            "❌ Я еще не знаю твой знак зодиака.\n"
            "Используй /setbirth чтобы указать дату рождения!"
        )
    
    await update.message.reply_text(response)

# Команда для обновления гороскопа
async def update_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    user_data = get_user_data(user.id)
    
    if user_data:
        zodiac_sign = user_data['zodiac_sign']
        
        # Очищаем кэш для этого знака
        horoscope_parser.clear_cache(zodiac_sign)
        
        await update.message.reply_text("🔄 Обновляю гороскоп...")
        
        # Получаем свежий гороскоп
        await get_my_horoscope(update, context)
    else:
        await update.message.reply_text("Сначала укажи дату рождения через /setbirth")

# Обработка неизвестных команд
async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Не понимаю эту команду.\n"
        "Используй /start чтобы увидеть список доступных команд."
    )

# Основная функция
def main():
    # Инициализируем базу данных
    init_database()
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setbirth", set_birth_date))
    application.add_handler(CommandHandler("mysign", get_my_sign))
    application.add_handler(CommandHandler("myhoroscope", get_my_horoscope))
    application.add_handler(CommandHandler("update", update_horoscope))
    
    # Обработчик для даты рождения
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^\d{2}\.\d{2}\.\d{4}$'), 
        handle_birth_date
    ))
    
    # Обработчик для неизвестных сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    
    # Запускаем бота
    print("🤖 Астробот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()