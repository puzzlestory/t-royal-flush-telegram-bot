from os import path
from json import load
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

CUR_CHALL_IDX = str()
SHOWS_CHOSEN_CHALL, CHOOSE_CHALL_TO_ANSWER = range(2)

DATA_DIR = path.join('.', 'game_data')

class Chall:
    def __init__(self, name, description, answer):
        self.name = name
        self.description = description
        self.answer = answer
        self.is_completed = False

DATA_PATH = path.join('game_data', 'game_data.json')

def load_data_from_csv():
    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    challs = dict()
    for c_idx, data in game_data.items():
        name_str = 'name'
        c_name = f'{c_idx} {data[name_str]}'
        chall = Chall(c_name, data['description'], data['answer'])
        challs[c_idx] = chall

    return challs

def start(update, context):
    welcome_txt = ['Hello, welcome to RoyalFlushBot!']
    welcome_txt.append('The bot of "Royal Flush: A Puzzle Story", a puzzle hunt game about playing cards, poker hands, kings, queens and brain challenges.\n[Early Access Version]')

    user_id = update.message.from_user.id
    context.chat_data[user_id] = load_data_from_csv()

    update.message.reply_text('\n'.join(welcome_txt))

def get_options_keyboard(data, user_id, mode):
    if not user_id in data.keys(): data[user_id] = load_data_from_csv()
    challs = data[user_id]

    if mode == 'TRY': names = [c.name for c in challs.values() if not c.is_completed]
    elif mode == 'SHOW': names = [f"{c.name} ✅" if c.is_completed else c.name for c in challs.values()]

    keyboard = list()
    for i in range(len(names))[::2]:
        line_keys = [InlineKeyboardButton(names[i], callback_data=names[i]),]
        if i + 1 < len(names):
            line_keys.append(InlineKeyboardButton(names[i + 1], callback_data=names[i + 1]))

        keyboard.append(line_keys)

    return InlineKeyboardMarkup(keyboard)

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

    chall_idx = query.data.split(' ')[0]
    challs = context.chat_data[user_id]

    name = challs[chall_idx].name.split(' ')
    name.remove(chall_idx)
    name = ' '.join(name)
    description = challs[chall_idx].description

    query.edit_message_text(text=f'Showing "{name}"\n')
    send_description(description, user_id, context.bot)

    return ConversationHandler.END

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

    chall_idx = query.data.split(' ')[0]
    challs = context.chat_data[user_id]

    name = challs[chall_idx].name.split(' ')
    name.remove(chall_idx)
    name = ' '.join(name)

    query.edit_message_text(text=f'Trying "{name}", type the answer')

    CUR_CHALL_IDX = chall_idx

    return CHOOSE_CHALL_TO_ANSWER

def check_answer(update, context):
    global CUR_CHALL_IDX

    user_id = update.message.from_user.id
    challs = context.chat_data[user_id]

    real_answer = challs[CUR_CHALL_IDX].answer
    user_answer = update.message.text.lower()

    if user_answer == real_answer:
        result = 'Right answer! Congratulations!'
        challs[CUR_CHALL_IDX].is_completed = True
    else:
        result = 'Wrong answer. Try again!'

    update.message.reply_text(result)

    CUR_CHALL_IDX = str()
    return ConversationHandler.END

show_command_handler = ConversationHandler(
    entry_points=[CommandHandler('show', show_challs)],
    states={
        SHOWS_CHOSEN_CHALL: [CallbackQueryHandler(choose_chall_to_show)],
    },
    fallbacks=[]
)

try_command_handler = ConversationHandler(
    entry_points=[CommandHandler('try', try_answer)],
    states={
        CHOOSE_CHALL_TO_ANSWER: [
            CallbackQueryHandler(choose_chall_to_answer),
            MessageHandler(Filters.text, check_answer)
        ]
    },
    fallbacks=[]
)