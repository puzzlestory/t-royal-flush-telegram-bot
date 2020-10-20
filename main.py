from os import path
from json import load, dump
from telegram.ext import Updater, CommandHandler

from env import TOKEN
from commands import start, show_command_handler, try_command_handler, Chall

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(show_command_handler)
    dp.add_handler(try_command_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print('=== BOT ATIVADO ===')
    print('Digite Ctrl + C para desativar.')
    main()
    print('=== BOT DESATIVADO ===')