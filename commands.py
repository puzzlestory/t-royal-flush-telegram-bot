from os import path
from json import load, dump

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

CUR_CHALL_IDX = str()
SHOWS_CHOSEN_CHALL, CHOOSE_CHALL_TO_ANSWER = range(2)

DATA_DIR = path.join('.', 'game_data')
DATA_PATH = path.join(DATA_DIR, 'game_data.json')

class Chall:
    def __init__(self, name, description, answer):
        self.name = name
        self.description = description
        self.answer = answer

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

def get_options_keyboard(data):
    challs = load_data_from_csv()
    data['challs'] = challs

    names = [c.name for c in challs.values()]
    keyboard = list()
    for i in range(len(names))[::2]:
        line_keys = [InlineKeyboardButton(names[i], callback_data=names[i]),]
        if i + 1 < len(names):
            line_keys.append(InlineKeyboardButton(names[i + 1], callback_data=names[i + 1]))

        keyboard.append(line_keys)

    return InlineKeyboardMarkup(keyboard)

def show_challs(update, context):
    reply_markup = get_options_keyboard(context.chat_data)
    update.message.reply_text('Choose a challenge to view', reply_markup=reply_markup)

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
    query.answer()
    chall_idx = query.data.split(' ')[0]

    challs = context.chat_data['challs']
    name = challs[chall_idx].name
    description = challs[chall_idx].description

    query.edit_message_text(text=f'Visu {name}\n')
    send_description(description, update.effective_user.id, context.bot)

    return ConversationHandler.END

def try_answer(update, context):
    reply_markup = get_options_keyboard(context.chat_data)
    update.message.reply_text('Choose a challenge to try', reply_markup=reply_markup)

    return CHOOSE_CHALL_TO_ANSWER

def choose_chall_to_answer(update, context):
    global CUR_CHALL_IDX
    query = update.callback_query
    query.answer()

    chall_idx = query.data.split(' ')[0]

    challs = context.chat_data['challs']
    name = challs[chall_idx].name
    query.edit_message_text(text=f'Tentando {name}, manda ae a resposta\n')

    CUR_CHALL_IDX = chall_idx

    return CHOOSE_CHALL_TO_ANSWER

def check_answer(update, context):
    global CUR_CHALL_IDX
    challs = context.chat_data['challs']

    real_answer = challs[CUR_CHALL_IDX].answer
    user_answer = update.message.text.lower()

    if user_answer == real_answer: result = 'Parabens otaro'
    else: result = 'Errou otaro'

    update.message.reply_text(result)

    CUR_CHALL_IDX = str()
    return ConversationHandler.END