from cmd_base import Chall, get_options_keyboard, save_user_progress, send_description, DATA_DIR
from json import loads, dumps
from os import path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


CHOOSE_CHALL, CHOOSE_OPTION, CHECK_ANSWER, CHOOSE_CONTINUE_OPTION = range(4)

# Não funciona atualmente por causa da query sem padrão
# def show_challs_menu_from_button(update, context):
#     query = update.callback_query
#     user_id = update.effective_user.id
#     query.answer()

#     reply_markup = get_options_keyboard(context.chat_data, user_id, mode='SHOW')
#     query.message.reply_text('Choose a challenge to view', reply_markup=reply_markup)

#     return CHOOSE_CHALL

def show_challs_menu(update, context):
    msg = update.message
    user_id = msg.from_user.id

    reply_markup = get_options_keyboard(context.chat_data, user_id, mode='SHOW')
    msg.reply_text('Choose a challenge to view', reply_markup=reply_markup)

    return CHOOSE_CHALL

def choose_chall(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    chall_idx = query.data
    challs = context.chat_data[user_id]
    context.user_data['cur_chall_idx'] = chall_idx

    name = challs[chall_idx].name

    description = challs[chall_idx].description

    bot = context.bot
    bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    #TODO: Botei esses nomes pro botões, mas eu sou ruim com nome ent mude
    keyboard = [[InlineKeyboardButton(text="Try chall 💬", callback_data="try"),
                 InlineKeyboardButton(text="Return to menu 🏠", callback_data="return")],
                [InlineKeyboardButton(text="Done ✔️", callback_data="done")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['last_description'] = send_description(description, user_id, bot)
    query.message.reply_text(text=f'Showing "{name}"\n', reply_markup=reply_markup)

    return CHOOSE_OPTION

def return_to_challs_menu(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    bot = context.bot

    try:
        last_description = context.user_data['last_description']
        bot.delete_message(chat_id=user_id, message_id=last_description.message_id)
    except:
        pass
    bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    reply_markup = get_options_keyboard(context.chat_data, user_id, mode='SHOW')
    query.message.reply_text('Choose a challenge to view', reply_markup=reply_markup)

    return CHOOSE_CHALL

def answer_chall(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    chall_idx = context.user_data['cur_chall_idx']
    challs = context.chat_data[user_id]

    name = challs[chall_idx].name
    query.edit_message_text(text=f'Trying "{name}", type the answer')

    return CHECK_ANSWER

def check_answer(update, context):
    user_id = update.message.from_user.id
    challs = context.chat_data[user_id]
    chall_idx = context.user_data['cur_chall_idx']

    right_answers = challs[chall_idx].answers
    user_answer = update.message.text.lower()

    #TODO: Novamente eu n sei escrever namoral =<
    keyboard = [[InlineKeyboardButton(text="Return to menu 🏠", callback_data="return"),
                 InlineKeyboardButton(text="Done ✔️", callback_data="done")]]
    
    if user_answer in right_answers:
        result = 'Right answer! Congratulations!'
        challs[chall_idx].is_completed = True
        save_user_progress(str(user_id), context)
    else:
        keyboard.insert(0, [InlineKeyboardButton(text="Try again 🔄", callback_data="try_again")])         
        result = 'Wrong answer, want to try again?'

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(result, reply_markup=reply_markup)

    return CHOOSE_CONTINUE_OPTION

def try_again(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text("Trying chall again, type the answer")

    return CHECK_ANSWER

def leave_challs_menu(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text("Bye-bye, see you later") #TODO
    return ConversationHandler.END

chall_menu = ConversationHandler(
    entry_points=[CommandHandler("challs", show_challs_menu)],
    states={
        CHOOSE_CHALL: [CallbackQueryHandler(choose_chall)],
        CHOOSE_OPTION: [
            CallbackQueryHandler(return_to_challs_menu, pattern="^return$"),
            CallbackQueryHandler(answer_chall, pattern="^try$")],
        CHECK_ANSWER: [MessageHandler(~Filters.regex('^/'), check_answer)],
        CHOOSE_CONTINUE_OPTION: [
            CallbackQueryHandler(try_again, pattern="^try_again$"),
            CallbackQueryHandler(return_to_challs_menu, pattern="^return$")]
    },
    fallbacks=[CallbackQueryHandler(leave_challs_menu, pattern="^done$")]
)
