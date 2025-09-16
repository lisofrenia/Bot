import os
import random
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7503700705:AAEXFMAoWj_CxpUbciu2Vf5XSr0qRtlYaDE"

# Список URL случайных изображений
RANDOM_IMAGE_URLS = [
    "https://avatars.mds.yandex.net/i?id=ee12572888d9938211c31c79eb9b7ecdad22f096-16971703-images-thumbs&n=13",
    "https://avatars.mds.yandex.net/i?id=6bf26c2270337e285ef945fe16108546f4eef490-4296724-images-thumbs&n=13",
    "https://avatars.mds.yandex.net/i?id=deea0acedc4187b7e29f01c9f9e1c4d7b6315353-5234690-images-thumbs&n=13",
    "https://avatars.mds.yandex.net/i?id=71436e914f324796f41e425e80a1395462b57246-5347001-images-thumbs&n=13"
]

# Функция для экранирования специальных символов MarkdownV2
def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

# Действие /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['📸 Отправить рандомное фото тигра'],
        ['✏️ Форматировать текст']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Выбери действие:\n"
        "• 📸 Отправить рандомное фото тигра\n"
        "• ✏️ Форматировать текст",
        reply_markup=reply_markup
    )

# Действие /send_random_photo
async def send_random_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Выбираем случайный URL
        random_url = random.choice(RANDOM_IMAGE_URLS)

        # Отправляем фото
        await update.message.reply_photo(
            photo=random_url,
            caption="Вот ваш случайный тигр ;) 📸"
        )

        logger.info(f"Отправлено фото: {random_url}")

    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await update.message.reply_text("Произошла ошибка при отправке фото 😢")

# Функции форматирования текста
def format_bold(text):
    return f"*{text}*"

def format_italic(text):
    return f"_{text}_"

def format_strikethrough(text):
    return f"~{text}~"

def format_code(text):
    return f"`{text}`"

def format_bold_italic(text):
    return f"*_{text}_*"

# Показ меню форматирования
async def show_format_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохраняем текст пользователя
    user_text = update.message.text
    context.user_data['original_text'] = user_text

    # Создаем инлайн-кнопки
    keyboard = [
        [
            InlineKeyboardButton("Жирный", callback_data="bold"),
            InlineKeyboardButton("Курсив", callback_data="italic")
        ],
        [
            InlineKeyboardButton("Перечеркнутый", callback_data="strike"),
            InlineKeyboardButton("Код", callback_data="code")
        ],
        [
            InlineKeyboardButton("Жирный курсив", callback_data="bold_italic")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📝 Ваш текст: {user_text}\n\n"
        "Выберите стиль форматирования:",
        reply_markup=reply_markup
    )

# Обработка нажатий на инлайн-кнопки
async def handle_format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    format_type = query.data
    original_text = context.user_data.get('original_text', '')

    if not original_text:
        await query.edit_message_text("Текст не найден. Попробуйте снова.")
        return

    # Применяем форматирование
    if format_type == "bold":
        formatted_text = format_bold(original_text)
        format_name = "жирный"
        parse_mode = 'MarkdownV2'
    elif format_type == "italic":
        formatted_text = format_italic(original_text)
        format_name = "курсив"
        parse_mode = 'MarkdownV2'
    elif format_type == "strike":
        formatted_text = format_strikethrough(original_text)
        format_name = "перечеркнутый"
        parse_mode = 'MarkdownV2'
    elif format_type == "code":
        formatted_text = format_code(original_text)
        format_name = "моноширинный"
        parse_mode = 'MarkdownV2'
    elif format_type == "bold_italic":
        formatted_text = format_bold_italic(original_text)
        format_name = "жирный курсив"
        parse_mode = 'MarkdownV2'

    # Кнопка для выбора другого стиля
    back_keyboard = [[InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="back")]]
    back_markup = InlineKeyboardMarkup(back_keyboard)

    # Экранируем текст для информационного сообщения
    escaped_original = escape_markdown(original_text)
    escaped_format_name = escape_markdown(format_name)

    # Отправляем результат с реальным форматированием
    await query.edit_message_text(
        f"✅ *Ваш текст отформатирован\\!*\n\n"
        f"*Оригинал:* {escaped_original}\n"
        f"*Стиль:* {escaped_format_name}\n\n"
        f"*Отформатированный текст:*",
        parse_mode='MarkdownV2',
        reply_markup=back_markup
    )

    # Отправляем само отформатированное сообщение
    await query.message.reply_text(
        formatted_text,
        parse_mode=parse_mode
    )

# Возврат к выбору стиля
async def handle_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    original_text = context.user_data.get('original_text', '')

    if not original_text:
        await query.edit_message_text("Текст не найден. Отправьте текст снова.")
        return

    # Создаем инлайн-кнопки
    keyboard = [
        [
            InlineKeyboardButton("Жирный", callback_data="bold"),
            InlineKeyboardButton("Курсив", callback_data="italic")
        ],
        [
            InlineKeyboardButton("Перечеркнутый", callback_data="strike"),
            InlineKeyboardButton("Код", callback_data="code")
        ],
        [
            InlineKeyboardButton("Жирный курсив", callback_data="bold_italic")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"Ваш текст: {original_text}\n\n"
        "Выберите стиль форматирования:",
        reply_markup=reply_markup
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '📸 Отправить рандомное фото тигра':
        await send_random_photo(update, context)
    elif text == '✏️ Форматировать текст':
        await update.message.reply_text(
            "📝 Отправьте текст, который хотите отформатировать:"
        )
    else:
        # Если это не команда, значит пользователь отправил текст для форматирования
        await show_format_menu(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_format_callback, pattern="^(bold|italic|strike|code|bold_italic)$"))
    application.add_handler(CallbackQueryHandler(handle_back_callback, pattern="^back$"))
    application.add_error_handler(error_handler)

    # Запускаем бота
    print("Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()