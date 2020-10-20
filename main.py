from os import path
from json import load, dump
from telegram.ext import Updater, CommandHandler

from env import TOKEN
from commands import show_command_handler, try_command_handler, Chall

def start(update, context):
    welcome_txt = ['Hello, welcome to RoyalFlushBot!']
    welcome_txt.append('The bot of "Royal Flush: A Puzzle Story", a puzzle hunt game about playing cards, poker hands, kings, queens and brain challenges.\n[Early Access Version]')

    update.message.reply_text('\n'.join(welcome_txt))

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