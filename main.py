from chall_menu import chall_menu
from env import TOKEN
from os import path
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def start(update, context):
    welcome_txt = ['Hello, welcome to Puzzle Story, a bot with puzzle hunt games to play free.\nAt the time, we are in Early Access of our first game, "Royal Flush: A Puzzle Story", with puzzles about playing cards, kings and queens.']
    welcome_txt.append('All the puzzles inside the same Act isn\'t in difficulty order yet. The answer of any puzzle is always a string of letters (no spaces, no numbers, no special characters).')
    welcome_txt.append('Have fun and thanks for the testing!')

    # Ainda não funciona
    # keyboard = [[InlineKeyboardButton(text="Show challs 📜", callback_data="show_challs")]]

    # reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('\n\n'.join(welcome_txt))

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(chall_menu)
    
    updater.start_polling()
    print("++++++++++ STARTING BOT +++++++++++")
    updater.idle()
    print("++++++++++  KILLING BOT  ++++++++++")


if __name__ == '__main__':
    print("Press CTRL + C to kill the bot")
    main()