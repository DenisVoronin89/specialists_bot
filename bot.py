from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    MessageHandler, 
    filters,
    ConversationHandler,
    CommandHandler
)
from config import BOT_TOKEN, AUTHORIZED_CHAT_ID
from registration import is_registered, register_teacher, get_teacher_name_by_id
from lessons import process_lesson_message

# Состояния для регистрации
FIO, PHONE, SUBJECT, CLASSES = range(4)

# Классы для выбора
CLASS_OPTIONS = [["начальные"], ["средние"], ["старшие"]]

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс регистрации"""
    await update.message.reply_text(
        "Добро пожаловать! Для регистрации введите ваше ФИО полностью (например: Иванов Иван Иванович):"
    )
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет ФИО и запрашивает телефон"""
    fio = update.message.text.strip()
    if len(fio) < 5:
        await update.message.reply_text("ФИО должно содержать минимум 5 символов. Попробуйте еще раз:")
        return FIO
    
    context.user_data['fio'] = fio
    await update.message.reply_text(
        "Введите ваш номер телефона (например: +79991234567):"
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет телефон и запрашивает предмет"""
    phone = update.message.text.strip()
    if not phone.startswith('+') or len(phone) < 10:
        await update.message.reply_text("Номер телефона должен начинаться с + и содержать минимум 10 цифр. Попробуйте еще раз:")
        return PHONE
    
    context.user_data['phone'] = phone
    await update.message.reply_text(
        "Введите предмет, который вы ведёте (например: Математика):"
    )
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет предмет и запрашивает классы"""
    context.user_data['subject'] = update.message.text
    
    keyboard = CLASS_OPTIONS
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "Выберите классы, которые вы ведёте:",
        reply_markup=reply_markup
    )
    return CLASSES

async def get_classes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершает регистрацию"""
    selected = update.message.text.strip()
    valid_classes = ["начальные", "средние", "старшие"]
    
    if selected not in valid_classes:
        await update.message.reply_text(
            "Пожалуйста, выберите один из предложенных вариантов классов:",
            reply_markup=ReplyKeyboardMarkup(CLASS_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
        )
        return CLASSES
    
    context.user_data['classes'] = selected
    
    # Регистрируем преподавателя
    user = update.effective_user
    registration_data = {
        "ФИО": context.user_data['fio'],
        "Номер телефона": context.user_data['phone'],
        "Телеграмм id": user.id,
        "Username": user.username or "",
        "Предмет": context.user_data['subject'],
        "Классы": context.user_data['classes']
    }
    
    try:
        register_teacher(registration_data)
    except Exception as e:
        await update.message.reply_text(
            f"Ошибка при регистрации: {str(e)}\nПопробуйте еще раз или обратитесь к администратору.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"Регистрация завершена! Добро пожаловать, {context.user_data['fio']}!\n\n"
        "Теперь вы можете отправлять сообщения с ФИО учеников для записи занятий.\n"
        "Формат: Фамилия Имя Класс Предмет / примечания\n"
        "Пример: Петров Петр 5 математика / хорошо подготовился",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Очищаем данные
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет регистрацию"""
    await update.message.reply_text(
        "Регистрация отменена. Отправьте любое сообщение для повторной регистрации.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения от пользователей"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Проверяем, что сообщение из авторизованного чата
    if chat_id != AUTHORIZED_CHAT_ID:
        return

    # Проверяем регистрацию
    if not is_registered(user.id):
        # Начинаем регистрацию сразу
        await update.message.reply_text(
            "👋 Добро пожаловать!\n\n"
            "Вы не зарегистрированы в системе. Для начала работы необходимо пройти регистрацию.\n\n"
            "Введите ваше ФИО полностью (например: Иванов Иван Иванович):"
        )
        return FIO

    # Если зарегистрирован, обрабатываем сообщение как занятие
    teacher_name = get_teacher_name_by_id(user.id)
    if teacher_name:
        try:
            response = process_lesson_message(teacher_name, update.message.text)
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"Ошибка при обработке сообщения: {str(e)}")
    else:
        await update.message.reply_text("Ошибка: не удалось найти данные преподавателя.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Бот работает только в авторизованном чате.")
        return

    if is_registered(user.id):
        teacher_name = get_teacher_name_by_id(user.id)
        await update.message.reply_text(
            f"Привет, {teacher_name}!\n\n"
            "Отправляйте сообщения с ФИО учеников для записи занятий.\n"
            "Формат: Фамилия Имя Класс Предмет / примечания\n"
            "Пример: Петров Петр 5 математика / хорошо подготовился"
        )
    else:
        await start_registration(update, context)


def main():
    """Основная функция запуска бота"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Создаем ConversationHandler для регистрации
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message),
            CommandHandler("start", start_command)
        ],
        states={
            FIO: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_fio)],
            PHONE: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_phone)],
            SUBJECT: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_subject)],
            CLASSES: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_classes)],
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
    )
    
    app.add_handler(conv_handler)
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
