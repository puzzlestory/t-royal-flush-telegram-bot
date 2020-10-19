from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from env import TOKEN
from commands import show, try_to_answer, check_answer, CHECK_ANSWER

def start(update, context):
    welcome_txt = ['Hello, welcome to RoyalFlushBot!']
    welcome_txt.append(
        'The bot of "Royal Flush: A Puzzle Story", a puzzle hunt game about \
        playing cards, poker hands, kings, queens and brain challenges. \
        [Early Access Version]'
    )

    update.message.reply_text('\n'.join(welcome_txt))

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('show', show))
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('try', try_to_answer)],
        states={
            CHECK_ANSWER: [MessageHandler(Filters.text, check_answer)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print('=== BOT ATIVADO ===')
    print('Digite Ctrl + C para desativar.')
    main()
    print('=== BOT DESATIVADO ===')