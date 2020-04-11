# coding: utf8
import lxml
import time
import logging
import requests
import telegram.ext
from covid import Covid
from threading import Timer
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Bot Logger')

Token = '1078084297:AAGhNxLhFkhinnZNozIowvp42CxZSrGCLqs'
updater = Updater(token=Token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher

target_url = 'https://стопкоронавирус.рф'

covid = Covid(source="worldometers")
response = requests.get(target_url)
covid_data = covid.get_data()

translator = Translator()

world_pos = 7
virusData = ""
country_list = []
listt = []
rus_country_list = []

in_emergancy_case = ['Мир', 'США', 'Испания', 'Италия', 'Германия', 'Франция', 'Иран', 'Великобритания', 'Турция', 'Швейцария', 'Бельгия', 'Нидерланды', 'Канада', 'Австрия', 'Бразилия', 'Португалия', 'Южная Корея', 'Израиль', 'Швеция', 'Россия', 'Норвегия', 'Австралия', 'Ирландия', 'Чехия', 'Чили', 'Индия',
                     'Дания', 'Польша', 'Румыния', 'Малайзия', 'Пакистан', 'Эквадор', 'Филиппины', 'Япония', 'Люксембург', 'Саудовская Аравия', 'Перу', 'Индонезия', 'Таиланд', 'Сербия', 'Финляндия', 'Мексика', 'ОАЭ', 'Панама', 'Катар', 'Доминиканская Республика', 'Греция', 'Южная Африка', 'Колумбия', 'Исландия',
                     'Аргентина', 'Алжир', 'Сингапур', 'Египет', 'Украина', 'Хорватия', 'Марокко', 'Эстония', 'Новая Зеландия', 'Ирак', 'Словения', 'Молдова', 'Гонконг', 'Литва', 'Армения', 'Бахрейн', 'Венгрия', 'Алмазная принцесса', 'Беларусь', 'Босния и Герцеговина', 'Кувейт', 'Казахстан', 'Камерун', 'Азербайджан',
                     'Тунис', 'Северная Македония', 'Болгария', 'Латвия', 'Ливан', 'Словакия', 'Андорра', 'Коста Рика', 'Кипр', 'Узбекистан', 'Уругвай', 'Албания', 'Тайвань', 'Катар', 'Буркина Фасо', 'Куба', 'Иордания', 'Реюньон', 'Оман', 'Нормандские острова', "Кот д'Ивуар", 'Гондурас', 'Сан-Марино', 'Палестина', 'Нигер',
                     'Вьетнам', 'Маврикий', 'Мальта', 'Нигерия', 'Черногория', 'Сенегал', 'Киргизия', 'Гана', 'Грузия', 'Боливия', 'Фарерские острова', 'Шри Ланка', 'Венесуэла', 'ДРК', 'Кения', 'Мартиника', 'Майотта', 'Остров Мэн', 'Гваделупа', 'Бруней', 'Генуа', 'Бангладеш', 'Камбоджа', 'Парагвай', 'Гибралтар', 'Тринидад и Тобаго',
                     'Руанда', 'Джибути', 'Мадагаскар', 'Лихтенштейн', 'Монако', 'Французская Гвиана', 'Аруба', 'Гватемала', 'Сальвадор', 'Барбадос', 'Ямайка', 'Того', 'Уганда', 'Мали', 'Конго', 'Эфиопия', 'Макао', 'Французская Полинезия', 'Бермудские острова', 'Каймановы острова', 'Замбия', 'Синт-Маартен', 'Сен-Мартен', 'Гайана', 'Эритрея',
                     'Багамские острова', 'Бенин', 'Габон', 'Гаити', 'Танзания', 'Мьянма', 'Сирия', 'Ливия', 'Мальдивы', 'Гвинея-Бисау', 'Новая Каледония', 'Ангола', 'Экваториальная Гвинея', 'Намибия', 'Антигуа и Барбуда', 'Доминика', 'Монголия', 'Либерия', 'Фиджи', 'Сент-Люсия', 'Кюрасао', 'Судан', 'Гренада', 'Лаос', 'Гренландия', 'Сейшельские острова',
                     'Суринам', 'Зимбабве', 'Мозамбик', 'Сент-Китс и Невис', 'Eswatini', 'М.С. Зандам', 'Непал', 'Чад', 'Теркс и Кайкос', 'ЦАР', 'Белиз', 'Кабо Верде', 'Ватикан', 'Сент-Винсент и Гренадины', 'Сомали', 'Ботсвана', 'Мавритания', 'Никарагуа', 'Монсеррат', 'Сен-Барт', 'Сьерра-Леоне', 'Бутан', 'Малави', 'Гамбия', 'Сан-Томе и Принсипи', 'Западная Сахара',
                     'Ангилья', 'Британские Виргинские острова', 'Бурунди', 'Карибские острова Нидерланды', 'Фолклендские острова', 'Папуа - Новая Гвинея', 'Saint Pierre & Miquelon', 'Южный Судан', 'Восточный Тимор', 'Китай']

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

print('Стартуем!')
curr_time = time.strftime("%H:%M:%S", time.localtime())
print(curr_time)
logger.info(f'Deploying time: {curr_time}')

'''
/////////// ФУНКЦИИ ОБНОВЛЕНИЯ ДАННЫХ ///////////
'''

def update_country_list():
    global country_list
    global rus_country_list
    for elem in covid_data:
        country_list.append(elem.get('country'))

    translations = translator.translate(country_list, dest='ru')

    for translation in translations:
        if translation.text == 'индюк':
            rus_country_list.append('турция')
        else:
            rus_country_list.append(translation.text.lower())

    for country in country_list:
        country_list[country_list.index(country)] = country.lower()


def daemon_covid_update():
    try:
        Timer(1200, daemon_covid_update).start()
        global covid
        covid = Covid(source="worldometers")
        global covid_data
        covid_data = covid.get_data()
        global response
        response = requests.get(target_url)
        update_country_list()
        if time.strftime("%H", time.localtime()) == '11':
            pass
        logger.info(f"{country_list[12]} \n {rus_country_list[12]}")
        logger.info("Data update done!")
    except:
        logger.error("Не удалось обновить данные!")


def get_data_by_country(country):
    if country in country_list:
        country_dict = covid.get_status_by_country_name(country)
        data = rus_country_list[country_list.index(country)].title() + '\n\n'

    elif country in rus_country_list:
        country_dict = covid.get_status_by_country_name(country_list[rus_country_list.index(country)])
        data = country.lower().title() + '\n\n'

    else:
        logger.error(f"{country.title()}-Такой страны не найдено")
        return f"{country.title()}-Такой страны не найдено"
    logger.info(f" Searching {country.title()}")
    i = 1

    while i < (len(countdown_name)):
        country_value = str(country_dict[worldometers_info[i - 1]])
        data += str(countdown_name[i]) + str(country_value) + '\n'
        i += 1
    return data


def parse_stopcorona():
    if response.status_code == 200:
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
        virusData = ''
        for el in countdown_name:
            virusData += str(el) + str(countdown_dict[el]) + '\n'
            i += 1
        logger.info(f"Parsing {target_url} done!")
        return virusData
    else:
        logger.error(f"Parsing Error! <status_code {response.status_code}>")
        return f"Parsing Error! <status_code {response.status_code}>"


def get_global_virus_data():
    global global_statistic_dict
    global_statistic_dict.update({countdown_name[1]: covid_data[world_pos].get(worldometers_info[0]),
                                  countdown_name[2]: covid_data[world_pos].get(worldometers_info[1]),
                                  countdown_name[3]: covid_data[world_pos].get(worldometers_info[2]),
                                  countdown_name[4]: covid_data[world_pos].get(worldometers_info[3])
                                  })
    i = 1
    global globalVirusData
    globalVirusData = ''
    while i < (len(countdown_name)):
        globalVirusData += str(countdown_name[i]) + str(global_statistic_dict[countdown_name[i]]) + '\n'
        i += 1
    return globalVirusData


'''
/////////// РАБОТА С БОТОМ ///////////
'''

reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Инфо по миру'), KeyboardButton(text='Инфо по России')],
            [KeyboardButton(text='Инфо по стране')  # , KeyboardButton(text='Месседж')
             ]
            ], resize_keyboard=True)


def get_inline_keyboard():
    inline_markup = [
                        [InlineKeyboardButton(text=rus_country_list[country_list.index('russia')].title(), callback_data='russia'), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[8])].title(), callback_data=country_list[8])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[9])].title(), callback_data=country_list[9]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[10])].title(), callback_data=country_list[10])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[11])].title(), callback_data=country_list[11]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[12])].title(), callback_data=country_list[12])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[13])].title(), callback_data=country_list[13]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[14])].title(), callback_data=country_list[14])],
                        [InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[15])].title(), callback_data=country_list[15]), InlineKeyboardButton(text=rus_country_list[country_list.index(country_list[16])].title(), callback_data=country_list[16])]
    ]
    return InlineKeyboardMarkup(inline_markup)


def send_message(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=context.job.context,
                             text='Сообщение')


def inline_keyboard_handler(update, context):
    query = update.callback_query
    data = query.data

    chat_id = update.effective_chat.id
    text = update.effective_message.text
    if data in country_list:
        country = data
        context.bot.send_message(chat_id=chat_id,
                                 text=get_data_by_country(country))
    else:
        print(data, "---Такой страны не найдено")


def start(update, context):
    logger.info(f"Bot started\n {update.effective_chat.id, update.effective_user.first_name}")
    context.bot.send_sticker(chat_id=update.effective_chat.id,
                             sticker=open('start_sticker.webp', 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Эй, " + update.effective_user.first_name + "!" + "\nЯ бот и я работаю!</b>\nДля получения информации нажми \n/info или отправь мне «Инфо»",
                             parse_mode='html')


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Если у вас есть предложения по улучшению бота, то напишите мне \n @Belshed",
                             parse_mode='html')


def info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Данные взяты с источников:\nwww.стопкоронавирус.рф\nwww.worldometers.info/coronavirus/\nЕсли у вас есть предложения по улучшению бота, то напишите мне \n @Belshed\n<b>Выбири что хочешь узнать⬇</b>\n",
                             reply_markup=reply_markup,
                             parse_mode='html')


def message(update, context):
    text = update.message.text.lower()
    if text == 'инфо':
        info(update, context)

    elif text == 'инфо по миру':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=get_global_virus_data())

    elif text == 'инфо по россии':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=parse_stopcorona())

    elif text == 'инфо по стране':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Выбери страну ⬇\nИли введи ее самостоятельно",
                                 reply_markup=get_inline_keyboard())

    elif text == 'ывпреврывапыупупё':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Возвращаемся назад",
                                 reply_markup=ReplyKeyboardRemove())

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
        job_minute = job_queue.run_once(send_minute, 1, context=update.effective_chat.id)
    else:
        logger.info(f"Message: {text}")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>Эй, " + update.effective_user.first_name + "!</b>\n" + "Ты написал(-а): <b>" + update.message.text + "</b>",
                                 parse_mode='html')


daemon_covid_update()

# job_minute = job_queue.run_repeating(send_minute, interval=60, first=0)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
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
