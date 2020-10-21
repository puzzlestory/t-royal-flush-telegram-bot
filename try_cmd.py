from json import loads, dumps
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from dpad_manager import read_dp, write_dp
from cmd_base import Chall, get_options_keyboard, PROGRESS_PATH

CUR_CHALL_IDX = str()
CHOOSE_CHALL_TO_ANSWER = range(1)

def try_answer(update, context):
    msg = update.message
    user_id = msg.from_user.id

    reply_markup = get_options_keyboard(context.chat_data, user_id, mode='TRY')
    msg.reply_text('Choose a challenge to try', reply_markup=reply_markup)

    return CHOOSE_CHALL_TO_ANSWER

def choose_chall_to_answer(update, context):
    global CUR_CHALL_IDX

    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    chall_idx = query.data
    challs = context.chat_data[user_id]

    name = challs[chall_idx].name
    query.edit_message_text(text=f'Trying "{name}", type the answer')

    CUR_CHALL_IDX = chall_idx

    return CHOOSE_CHALL_TO_ANSWER

def save_user_progress(user_id):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
    else:
        user_progress = list()

    user_progress.append(CUR_CHALL_IDX)
    user_data_str = dumps({'progress': user_progress}, indent=2)
    write_dp(user_id, user_data_str)

def check_answer(update, context):
    global CUR_CHALL_IDX

    user_id = update.message.from_user.id
    challs = context.chat_data[user_id]

    right_answers = challs[CUR_CHALL_IDX].answers
    user_answer = update.message.text.lower()

    if user_answer in right_answers:
        result = 'Right answer! Congratulations!'
        challs[CUR_CHALL_IDX].is_completed = True
        save_user_progress(str(user_id))
    else:
        result = 'Wrong answer, /try again!'

    update.message.reply_text(result)

    CUR_CHALL_IDX = str()
    return ConversationHandler.END

try_command_handler = ConversationHandler(
    entry_points=[CommandHandler('try', try_answer)],
    states={
        CHOOSE_CHALL_TO_ANSWER: [
            CallbackQueryHandler(choose_chall_to_answer),
            MessageHandler(~Filters.regex('^/'), check_answer)
        ]
    },
    fallbacks=[]
)