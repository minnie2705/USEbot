import random
import mysql.connector
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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
    await update.message.reply_text(
        f"Приветствую! "
        f"Я бот-помощник для подготовки к ЕГЭ по обществознанию! \n"
        f"Выберите, что вы сейчас хотите 👇", reply_markup=reply_markup)

    print("Sent reply to /start command")
    return FIRST


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
        ],
        [
            InlineKeyboardButton("🔎К выбору типа задания", callback_data='choose_type'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "Хотите начать решать задания?", reply_markup=reply_markup
    )

    return FIRST


async def stop(update: Update, context):
    print("Received /stop command")
    keyboard = [
        [
            InlineKeyboardButton("Начать снова", callback_data='start_again'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'Всего доброго! \n'
                                    f'Если снова захочешь решать, нажми на кнопку ниже или напиши /start.',
                                    reply_markup=reply_markup)
    return ConversationHandler.END


async def end(update: Update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Начать снова", callback_data='start_again'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f'Всего доброго! \n'
                                  f'Если снова захочешь решать, нажми на кнопку ниже или напиши /start.',
                                  reply_markup=reply_markup)
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
        host='localhost',
        user='root',
        password='MinMin123',
        database='ege'
    )
    cursor = connection.cursor()

    query = f'SELECT id_example FROM examples WHERE type_number = {selected_type}'
    cursor.execute(query)
    ids = [row[0] for row in cursor.fetchall()]
    if not ids:
        await query.edit_message_text(f'Не найдено заданий для типа {selected_type}. Попробуйте выбрать другой тип.')
        return FIRST

    N_EXAMPLE = random.choice(ids)

    query = f'SELECT question, answer, right_answer FROM examples WHERE id_example = {N_EXAMPLE}'
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        question_text, ANSWER, EXPLANATION = result
        await update.callback_query.edit_message_text(f"*Задание № {N_EXAMPLE}*\n {question_text}",
                                                      parse_mode='Markdown')
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


def main():
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()
    print("Application built...")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
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

    application.add_handler(conv_handler)
    print("Handler added...")

    application.run_polling()
    print("Bot is polling...")


if __name__ == '__main__':
    main()
