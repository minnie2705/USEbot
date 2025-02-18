import random
import mysql.connector
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, ConversationHandler, filters
import data_loader  # Импортируем файл data_loader

TOKEN = '7891116502:AAEyEMUVfoN5X0LY4JnkFds2v8-SMt9qhxk'
ANSWER = ''
EXPLANATION = ''
N_EXAMPLE = ''
# Этапы/состояния разговора
FIRST, SECOND = range(2)
# Данные обратного вызова
NEXT, END = range(2)

async def start(update: Update, context):
    print("Received /start command")
    keyboard = [
        [
            InlineKeyboardButton("Решать задания", callback_data=str(NEXT)),
        ],
        [
            InlineKeyboardButton("Прекратить", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Приветствую! "
        f"Я бот-помощник для подготовки к ЕГЭ по обществознанию! \n"
        f"Выберите, что вы сейчас хотите 👇", reply_markup=reply_markup)

    print("Sent reply to /start command")
    return FIRST

async def stop(update: Update, context):
    print("Received /stop command")
    await update.message.reply_text(f'Всего доброго! \n'
                                    f'Если снова захочешь решать, нажми или напиши /start')
    return ConversationHandler.END

async def end(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f'Всего доброго! \n'
                                       f'Если снова захочешь решать, нажми или напиши /start')
    return ConversationHandler.END

async def next_example(update: Update, context):
    global ANSWER, EXPLANATION, N_EXAMPLE
    print("Fetching next example")
    query = update.callback_query
    await query.answer()

    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='MinMin123',
        database='user_base'
    )
    cursor = connection.cursor()

    query = 'SELECT id_example FROM examples'
    cursor.execute(query)
    ids = [row[0] for row in cursor.fetchall()]
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
        await update.callback_query.message.reply_text(f"✍ Напишите *ответ* на задание. "
                                                       f"Если ответов несколько, укажите их через *пробел*",
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
            InlineKeyboardButton("🤓Следующее задание‍", callback_data=str(NEXT)),
            InlineKeyboardButton("😩 Хватит", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="👇 Выбирайте 👇", reply_markup=reply_markup
    )
    return FIRST

def main():
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()
    print("Application built...")

    # Загружаем данные из сайта, если они еще не загружены
    data_loader.load_data()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(next_example, pattern='^' + str(NEXT) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$')
            ],
            SECOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer)],  # Используем filters.COMMAND
        },
        fallbacks=[CommandHandler('stop', stop)],  # Для команды /stop
        per_chat=True  # Устанавливаем параметр per_chat
    )

    application.add_handler(conv_handler)
    print("Handler added...")

    application.run_polling()
    print("Bot is polling...")

if __name__ == '__main__':
    main()
