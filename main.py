from os import path
from json import load, dump
from telegram.ext import Updater, CommandHandler

from env import TOKEN
from commands import show_command_handler, try_command_handler, Chall

def start(update, context):
    welcome_txt = ['Hello, welcome to Puzzle Story, a bot with puzzle hunt games to play free.\nAt the time, we are in Early Access of our first game, "Royal Flush: A Puzzle Story", with puzzles about playing cards, kings and queens.']
    welcome_txt.append('All the puzzles inside the same Act isn\'t in difficulty order yet. The answer of any puzzle is always a string of letters (no spaces, no numbers, no special characters).')
    welcome_txt.append('Have fun and thanks for the testing!')

    update.message.reply_text('\n\n'.join(welcome_txt))

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(show_command_handler)
    dp.add_handler(try_command_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Press CTRL + C to kill the bot")
    main()
