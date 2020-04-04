from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

Token = '1078084297:AAGhNxLhFkhinnZNozIowvp42CxZSrGCLqs'
updater = Updater(token=Token, use_context=True)
dispatcher = updater.dispatcher

help_button = 'Помощь'