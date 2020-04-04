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

covid = Covid(source="worldometers")
response = requests.get(target_url)
covid_data = covid.get_data()
world_pos = 0

print('Стартуем!')

countdown_name =    [
                     "Проведено тестов: ",
                     "Случаев заболевания: ",
                     "Случай заболевания за последние сутки: ",
                     "Человек выздоровело: ",
                     "Человек умерло: "
                    ]

worldometers_info = [
    "confirmed",
    "new_cases",
    "recovered",
    "deaths"
]
country_list = []
global_statistic_dict = {}
global_statistic_dict.update({countdown_name[1]: covid_data[world_pos].get(worldometers_info[0]),
                              countdown_name[2]: covid_data[world_pos].get(worldometers_info[1]),
                              countdown_name[3]: covid_data[world_pos].get(worldometers_info[2]),
                              countdown_name[4]: covid_data[world_pos].get(worldometers_info[3])})


def get_data_by_country(country):
    country_dict = covid.get_status_by_country_name(country)
    data = country + '\n'
    i = 1
    while i < (len(countdown_name)):
        data += str(countdown_name[i]) + str(country_dict[worldometers_info[i - 1]]) + '\n'
        i += 1
    print(data)
    return data


for elem in covid_data:
    country_list.append(elem.get('country'))

if response.status_code == 200:
    page = response.content
    html = BeautifulSoup(page, 'html.parser')

    item = ''
    counter = 0
    countdown_dict = {}
    for elem in html.select('.cv-countdown__item'):
        value = elem.span.get_text()
        countdown_dict[countdown_name[counter]] = value
        counter += 1

    globalVirusData = ""
    i = 1
    while i < (len(countdown_name)):
        globalVirusData += str(countdown_name[i]) + str(global_statistic_dict[countdown_name[i]]) + '\n'
        i += 1

    virusData = ""
    i = 0
    for el in countdown_name:
        virusData += str(el) + str(countdown_dict[el]) + '\n'
        i += 1

reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Инфо по миру'), KeyboardButton(text='Инфо по России')],
            [KeyboardButton(text='Инфо по стране'), KeyboardButton(text='Назад')]
            ], resize_keyboard=True)


def start(update, context):
    context.bot.send_sticker(chat_id=update.effective_chat.id,
                             sticker=open('start_sticker.webp', 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Эй, " + update.effective_user.first_name + "!" + "\nЯ бот и я работаю!</b>",
                             parse_mode='html')


def message(update, context):
    text = update.message.text
    if text.lower() == 'инфо':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>Выбири что хочешь узнать:</b>\n",
                                 reply_markup=reply_markup,
                                 parse_mode='html')

    elif text.lower() == 'инфо по миру':
        context.bot.send_message(chat_id=update.effective_chat.id, text=globalVirusData)

    elif text.lower() == 'инфо по россии':
        context.bot.send_message(chat_id=update.effective_chat.id, text=virusData)

    elif text.lower() == 'инфо по стране':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Выбери страну",
                                 reply_markup=ReplyKeyboardRemove())

    elif text.lower() == 'назад':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=ReplyKeyboardRemove())

    elif country_list.index(text.lower().title()) >= 0:
        country = text.lower().title()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=get_data_by_country(country),
                                 parse_mode='html')

    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>Эй, " + update.effective_user.first_name + "!</b>\n" + "Ты написал(-а): <b>" + update.message.text + "</b>",
                                 parse_mode='html')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.all, message)
dispatcher.add_handler(message_handler)

updater.start_polling()
updater.idle()
