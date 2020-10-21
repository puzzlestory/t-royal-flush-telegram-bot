from os import path
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from cmd_base import Chall, get_options_keyboard,  DATA_DIR

SHOWS_CHOSEN_CHALL = range(1)

def show_challs(update, context):
    msg = update.message
    user_id = msg.from_user.id

    reply_markup = get_options_keyboard(context.chat_data, user_id, mode='SHOW')
    msg.reply_text('Choose a challenge to view', reply_markup=reply_markup)

    return SHOWS_CHOSEN_CHALL

def send_description(description, chat_id, bot):
    for d_filename in description:
        d_filename = path.join(DATA_DIR, d_filename)

        if d_filename.endswith('.jpg'):
            d_photo = open(d_filename, 'rb')
            bot.send_photo(chat_id=chat_id, photo=d_photo)
        elif d_filename.endswith('.txt'):
            d_txt = open(d_filename).read()
            bot.send_message(chat_id=chat_id, text=f'<code>{d_txt}</code>', parse_mode='HTML')

def choose_chall_to_show(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    chall_idx = query.data
    challs = context.chat_data[user_id]

    name = challs[chall_idx].name
    description = challs[chall_idx].description

    bot = context.bot
    bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    bot.send_message(chat_id=user_id, text=f'Showing "{name}"\n')
    send_description(description, user_id, bot)

    return ConversationHandler.END

show_command_handler = ConversationHandler(
    entry_points=[CommandHandler('show', show_challs)],
    states={
        SHOWS_CHOSEN_CHALL: [CallbackQueryHandler(choose_chall_to_show)],
    },
    fallbacks=[]
)