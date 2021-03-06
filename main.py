# coding: utf8
import time
import logging
import requests
import telegram.ext
from numpy import random
from threading import Timer
from bs4 import BeautifulSoup
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b %H:%M:%S')
logger = logging.getLogger('Bot Logger')

fh = logging.FileHandler('bot_logs.log', mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)


# Token = '1078084297:AAGhNxLhFkhinnZNozIowvp42CxZSrGCLqs'  # Old Bot#
Token = '1283232360:AAGboP5rZqefNicAolAa2h0lPJYSeN_ewws'  # New Bot
key = 'trnsl.1.1.20200423T190856Z.24eca77935c90552.f3fcbb20deda0ee7992f70687c290b13a93e0d66'
translate_url = "https://translate.yandex.net/api/v1.5/tr.json/translate"

updater = Updater(token=Token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher
proxy_dict = {}

world_pos = 7
virusData = ""
country_list = []
rus_country_list = []

countdown_dict = {}
globalVirusData = ""
global_statistic_dict = {}

countdown_name =    [
                     "Проведено тестов: ",
                     "Случаев заболевания: ",
                     "Случаев заболевания за сегодня: ",
                     "Человек выздоровело: ",
                     "Человек умерло: "
                    ]

worldometers_info = [
                    "confirmed",
                    "new_cases",
                    "recovered",
                    "deaths"
                    ]

covid_dict = {}
socks_arr = []

logger.info('Стартуем!')
curr_time = time.strftime("%H:%M:%S", time.localtime())
logger.info(f' Deploying time: {curr_time}')

'''
/////////// ФУНКЦИИ ОБНОВЛЕНИЯ ДАННЫХ ///////////
'''


def ya_translate(text):

    params = {
        "key": key,
        "text": text,
        "lang": 'en-ru'
    }
    response = requests.get(translate_url, params=params)
    return response.json().get("text")


def update_country_list():

    global country_list
    global rus_country_list
    try:
        translations = []
        try:
            translations = ya_translate(country_list)
        except:
            logger.error("Ошибка в переводе!", exc_info=True)

        for translation in translations:
            rus_country_list.append(translation.lower())
        for country in country_list:
            country_list[country_list.index(country)] = country.lower()
    except:
        logger.error("Ошибка в составлении списков стран!", exc_info=True)


def daemon_covid_update():
    Timer(3600, daemon_covid_update).start()
    parse_worldometers()
    update_country_list()
    if time.strftime("%H", time.localtime()) == '11':
        pass
    rand = random.randint(len(country_list))
    logger.info(f" {country_list[rand]}, {rus_country_list[rand]}")
    logger.info(" Bot is active!")


def get_status_by_country_name(country):
    response = covid_dict.get(country.lower())
    return response


def get_data_by_country(country):
    if country in country_list:
        country_dict = get_status_by_country_name(country)
        data = rus_country_list[country_list.index(country)].title() + '\n\n'

    elif country in rus_country_list:
        country_dict = get_status_by_country_name(country_list[rus_country_list.index(country)])
        data = country.lower().title() + '\n\n'

    else:
        logger.error(f" {country}-Такой страны не найдено")
        return f" {country}-Такой страны не найдено"
    logger.info(f" Searching {country.title()}")
    i = 1

    while i < (len(countdown_name)):
        country_value = str(country_dict[worldometers_info[i - 1]])
        data += str(countdown_name[i]) + str(country_value) + '\n'
        i += 1
    return data


def parse_worldometers():
    resp = requests.get("https://www.worldometers.info/coronavirus/")
    try:
        page = resp.text
        html = BeautifulSoup(page, "lxml")
        table = html.find("table", attrs={"id": "main_table_countries_today"})
        headers = ["country",
                   "confirmed",
                   "new_cases",
                   "deaths",
                   "new_deaths",
                   "recovered",
                   "active",
                   "total_tests"
                   ]
        rows = table.find('tbody').select('tr')

        def fill_dict(position):
            i = 0
            dict = {}
            while i < 7:
                dict[headers[i]] = rows[position].find_all('td')[i + 1].text.strip().replace(",", " ").replace("+", "")
                i += 1
            dict[headers[i]] = rows[position].find_all('td')[10].text.strip().replace(",", " ").replace("+", "").lower()
            return dict

        i = world_pos
        while i < len(rows):
            covid_dict[rows[i].find_all('td')[1].text.lower()] = fill_dict(i)
            country_list.append(rows[i].find_all('td')[1].text)
            i += 1
        logger.info("Worldometers parsed!")
    except:
        logger.error("Ошибка парсинга Worldometers", exc_info=True)


def parse_stopcorona():
    target_url = 'https://стопкоронавирус.рф'

    response = requests.get(target_url)
    try:
        page = response.content
        html = BeautifulSoup(page, 'lxml')

        counter = 0
        for elem in html.select('.cv-countdown__item'):
            value = elem.span.get_text()
            global countdown_dict
            countdown_dict[countdown_name[counter]] = value
            counter += 1

        i = 0
        global virusData
        virusData = 'Россия\n\n'
        for el in countdown_name:
            virusData += str(el) + str(countdown_dict[el]) + '\n'
            i += 1
        logger.info("StopCorona parsed!")
        response.close()
        return virusData
    except:
        logger.error(f"Parsing Error! <status_code {response.status_code}>", exc_info=True)
        return f"Parsing Error! <status_code {response.status_code}>"


def parse_proxy_site():
    url = 'https://2ip.ru/proxy/'
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 OPR/67.0.3575.115',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    response = session.get(url=url)
    if response.status_code == 200:
        page = response.content
        html = BeautifulSoup(page, 'lxml')
        table = html.find('table')
        rows = table.find_all('tr')
        for row in rows:
            if row.find('img', attrs={'alt': 'ON'}):
                socks_arr.append(row.find('td').text.split()[0])


'''
/////////// РАБОТА С БОТОМ ///////////
'''

reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Инфо по миру'), KeyboardButton(text='Инфо по России')],
            [KeyboardButton(text='Инфо по стране')  # , KeyboardButton(text='Месседж')
             ]
            ], resize_keyboard=True)


def get_sources_markup():
    souses_markup = [[InlineKeyboardButton(text='WorldoMeters', url='www.worldometers.info/coronavirus/'), InlineKeyboardButton(text='СтопКоронавирус', url='www.стопкоронавирус.рф')]]
    return InlineKeyboardMarkup(souses_markup)


def get_inline_keyboard():
    inline_markup = [
                        [InlineKeyboardButton(text=rus_country_list[country_list.index('russia')].title(), callback_data='russia'), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[1])].upper(), callback_data=country_list[1])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[2])].title(), callback_data=country_list[2]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[3])].title(), callback_data=country_list[3])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[4])].title(), callback_data=country_list[4]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[5])].title(), callback_data=country_list[5])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[6])].title(), callback_data=country_list[6]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[7])].title(), callback_data=country_list[7])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[8])].title(), callback_data=country_list[8]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[9])].title(), callback_data=country_list[9])]
    ]
    return InlineKeyboardMarkup(inline_markup)


def send_message(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=context.job.context,
                             text='Сообщение')


def inline_keyboard_handler(update, context):
    query = update.callback_query
    data = query.data

    chat_id = update.effective_chat.id
    if data in country_list:
        country = data
        context.bot.send_message(chat_id=chat_id,
                                 text=get_data_by_country(country))
    else:
        logger.error(data, "---Такой страны не найдено")


def start(update, context):
    logger.info(f"Bot started\n {update.effective_chat.id, update.effective_user.first_name}")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Эй, " + update.effective_user.first_name + "!" + "\nЯ бот со статистикой по коронавирусу и я работаю!</b>\nДля получения информации нажми \n/info или отправь мне «Инфо»",
                             parse_mode='html')


def about(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Если у вас есть предложения по улучшению бота, то напишите мне: @Belshed\n\nДанные взяты с источников⬇",
                             reply_markup=get_sources_markup(),
                             parse_mode='html')


def info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Выбири что хочешь узнать⬇</b>\n",
                             reply_markup=reply_markup,
                             parse_mode='html')


def message(update, context):
    text = update.message.text.lower()
    if text == 'инфо':
        info(update, context)

    elif text == 'инфо по миру':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=get_data_by_country('world'))

    elif text == 'инфо по россии':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=parse_stopcorona())

    elif text == 'инфо по стране':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Выбери страну ⬇\nИли введи ее самостоятельно",
                                 reply_markup=get_inline_keyboard())

    elif text in country_list:
        country = text
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=get_data_by_country(country),
                                 parse_mode='html')

    elif text in rus_country_list:
        country = text
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=get_data_by_country(country),
                                 parse_mode='html')
    elif text == 'месседж':
        job_queue.run_once(send_message, 1, context=update.effective_chat.id)

    else:
        logger.info(f" Message: {text}")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>Эй, " + update.effective_user.first_name + "!</b>\n" + "Ты написал(-а): <b>" + update.message.text + "</b>",
                                 parse_mode='html')


daemon_covid_update()

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('about', about)
dispatcher.add_handler(help_handler)

info_handler = CommandHandler('info', info)
dispatcher.add_handler(info_handler)

message_handler = MessageHandler(Filters.all, message)
dispatcher.add_handler(message_handler)

buttons_handler = CallbackQueryHandler(callback=inline_keyboard_handler,
                                       pass_chat_data=True)
dispatcher.add_handler(buttons_handler)

updater.start_polling()
updater.idle()
