import requests
from covid import Covid
from bs4 import BeautifulSoup
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

Token = '1078084297:AAGhNxLhFkhinnZNozIowvp42CxZSrGCLqs'
updater = Updater(token=Token, use_context=True)
dispatcher = updater.dispatcher

help_button = 'Помощь'


target_url = 'https://стопкоронавирус.рф'

covid = Covid()
response = requests.get(target_url)
# covid_data = covid.get_data()


if response.status_code == 200:
    page = response.content
    html = BeautifulSoup(page, 'html.parser')

    item = ''
    counter = 0
    countdown_name = [
                 "Проведено тестов: ",
                 "Случаев заболевания: ",
                 "Случай заболевания за последние сутки: ",
                 "Человек выздоровело: ",
                 "Человек умерло: "
                 ]
    countdown_dict = {}
    for elem in html.select('.cv-countdown__item'):
        value = elem.span.get_text()
        countdown_dict[countdown_name[counter]] = value
        counter += 1

    print(countdown_dict)


reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Инфо по миру'), KeyboardButton(text='Инфо по России')],
            [KeyboardButton(text='Инфо по стране'), KeyboardButton(text='Назад')]
            ], resize_keyboard=True)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Эй, " + update.effective_user.first_name + "!" + "\nЯ бот и я работаю!")


def message(update, context):
    text = update.message.text

    if text.lower() == 'инфо':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Выбири что хочешь узнать:\n", reply_markup=reply_markup)
    elif text.lower() == 'инфо по миру':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Актуальная информация по коронавирусу в мире\n")
    elif text.lower() == 'инфо по россии':
        data = ''
        i = 0
        for el in countdown_name:
            data += str(countdown_name[i]) + str(countdown_dict[countdown_name[i]]) + '\n'
            i += 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=data)
    elif text.lower() == 'инфо по стране':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Актуальная информация по коронавирусу в стране\n")
    elif text.lower() == 'назад':
        context.bot.send_message(chat_id=update.effective_chat.id, text="", reply_markup=ReplyKeyboardRemove())
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Эй, " + update.effective_user.first_name + "!\n" + "Ты написал: " + update.message.text)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.all, message)
dispatcher.add_handler(message_handler)

updater.start_polling()
