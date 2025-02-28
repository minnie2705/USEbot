import os
import random
import mysql.connector
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, ConversationHandler, filters

TOKEN = '7891116502:AAEyEMUVfoN5X0LY4JnkFds2v8-SMt9qhxk'
ANSWER = ''
EXPLANATION = ''
N_EXAMPLE = ''
FIRST, SECOND, TYPE_SELECTION = range(3)
NEXT, END = range(2)


async def start(update: Update, context):
    print("Received /start command")
    keyboard = [
        [
            InlineKeyboardButton("Выбрать тип задания", callback_data='choose_type'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Создаем кнопки с командами для клавиатуры
    menu_keyboard = [
        [KeyboardButton("/start"), KeyboardButton("/stop")]
    ]
    menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Приветствую! Я бот-помощник для подготовки к ЕГЭ по обществознанию! \n",
        reply_markup=reply_markup
    )
    await update.message.reply_text(
        "Используйте кнопки ниже для управления ботом.",
        reply_markup=menu_markup
    )

    print("Sent reply to /start command")
    return FIRST

# Обработчик команды /stop
async def stop(update: Update, context):
    print("Received /stop command")
    await update.message.reply_text(f'Всего доброго! \n'
                                    f'Если снова захочешь решать, нажми на кнопку ниже или напиши /start.')
    return ConversationHandler.END

# Обработчик выбора типа задания
async def choose_type(update: Update, context):
    print("Choosing task type")
    keyboard = [
        [InlineKeyboardButton(f"{i}", callback_data=str(i)) for i in range(1, 5)],
        [InlineKeyboardButton(f"{i}", callback_data=str(i)) for i in range(5, 9)],
        [InlineKeyboardButton(f"{i}", callback_data=str(i)) for i in range(9, 13)],
        [InlineKeyboardButton(f"{i}", callback_data=str(i)) for i in range(13, 17)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Выберите тип задания:", reply_markup=reply_markup
    )
    return TYPE_SELECTION

async def set_task_type(update: Update, context):
    query = update.callback_query
    selected_type = int(query.data)
    context.user_data['task_type'] = selected_type

    await query.answer()
    await query.edit_message_text(text=f"Вы выбрали тип задания: {selected_type}")

    keyboard = [
        [
            InlineKeyboardButton("✍Решать задания", callback_data=str(NEXT)),
        ],
        [
            InlineKeyboardButton("⬅️Назад", callback_data='choose_type'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "Хотите начать решать задания?", reply_markup=reply_markup
    )

    return FIRST


#async def stop(update: Update, context):
    #print("Received /stop command")
   # await update.message.reply_text(f'Всего доброго! \n'
                                    #f'Если снова захочешь решать, нажми на кнопку ниже или напиши /start.')
    #return ConversationHandler.END


async def end(update: Update, context):
    query = update.callback_query
    await query.answer()


    await query.edit_message_text(f'Всего доброго! \n'
                                  f'Если снова захочешь решать, нажми на кнопку ниже или напиши /start.')
    return ConversationHandler.END


async def next_example(update: Update, context):
    global ANSWER, EXPLANATION, N_EXAMPLE
    print("Fetching next example")
    query = update.callback_query
    await query.answer()

    selected_type = context.user_data.get('task_type', None)
    if selected_type is None:
        await query.edit_message_text('Ошибка: не выбран тип задания. Пожалуйста, выберите тип.')
        return FIRST

    connection = mysql.connector.connect(
        host='host.docker.internal',
        user='root',
        password='MinMin123',
        database='user_base'
    )
    cursor = connection.cursor()

    query = f'SELECT id_example, image_path FROM examples WHERE type_number = {selected_type}'
    cursor.execute(query)
    rows = cursor.fetchall()
    if not rows:
        await query.edit_message_text(f'Не найдено заданий для типа {selected_type}. Попробуйте выбрать другой тип.')
        return FIRST

    N_EXAMPLE, image_path = random.choice(rows)

    query = f'SELECT question, answer, right_answer FROM examples WHERE id_example = {N_EXAMPLE}'
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        question_text, ANSWER, EXPLANATION = result
        await update.callback_query.edit_message_text(f"*Задание № {N_EXAMPLE}*\n {question_text}",
                                                      parse_mode='Markdown')

        if selected_type == 9 and image_path:
            # Убираем символы новой строки и пробелы в конце пути
            image_path = image_path.rstrip('\n')

            # Путь к изображению в локальной папке 'images'
            image_file_path = os.path.join('images', image_path)

            # Проверяем существование файла перед отправкой
            if os.path.exists(image_file_path):
                await update.callback_query.message.reply_photo(photo=open(image_file_path, 'rb'))
            else:
                await update.callback_query.message.reply_text(
                    f"Ошибка: изображение не найдено по пути: {image_file_path}")

        await update.callback_query.message.reply_text(f"✍ Напишите *ответ* на задание. ",
                                                       parse_mode='Markdown')
        print("Sent example question and answer request")
        return SECOND
    else:
        await update.callback_query.edit_message_text('Ошибка получения задания. Попробуйте снова.')


async def answer(update: Update, context):
    global ANSWER, EXPLANATION, N_EXAMPLE
    print("Received answer")
    user_answer = update.message.text.strip()
    if user_answer == ANSWER:
        await update.message.reply_text(f'🥰 Правильно, ответ: {ANSWER}')
    else:
        await update.message.reply_text(f'🥺 Неправильно, ответ: {ANSWER}\nПояснение: {EXPLANATION}')

    keyboard = [
        [
            InlineKeyboardButton("🤓Следующее задание‍)", callback_data=str(NEXT)),
            InlineKeyboardButton("🔎К выбору типа задания", callback_data='choose_type'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="👇 Выбирайте 👇", reply_markup=reply_markup
    )
    return FIRST


async def start_again(update: Update, context):
    query = update.callback_query
    await query.answer()

    await query.message.bot.send_message(chat_id=update.effective_chat.id, text='/start')


async def start_button(update: Update, context):
    # Когда нажимается кнопка /start
    return await start(update, context)  # Перезапуск команды /start

# Основная функция для запуска бота
def main():
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()
    print("Application built...")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # Для /start
        states={
            FIRST: [
                CallbackQueryHandler(choose_type, pattern='^choose_type$'),
                CallbackQueryHandler(next_example, pattern='^' + str(NEXT) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start_again, pattern='^start_again$'),
            ],
            TYPE_SELECTION: [CallbackQueryHandler(set_task_type)],
            SECOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer)],
        },
        fallbacks=[CommandHandler('stop', stop)],
        per_chat=True
    )

    # Добавляем обработчик кнопки /start
    application.add_handler(CallbackQueryHandler(start_button, pattern='^/start$'))

    application.add_handler(conv_handler)
    print("Handler added...")

    application.run_polling()
    print("Bot is polling...")

if __name__ == '__main__':
    main()
