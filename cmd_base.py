from os import path
from json import load, loads, dump, dumps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from dpad_manager import read_dp, write_dp

DATA_DIR = path.join('.', 'game_data')
DATA_PATH = path.join(DATA_DIR, 'game_data.json')
PROGRESS_PATH = path.join('.', 'users_progress', 'users_progress.json')

class Chall:
    def __init__(self, idx, name, description, answers):
        self.idx = idx
        self.name = name
        self.title = f'{idx} {name}'
        self.description = description
        self.answers = answers
        self.is_completed = None

def set_progress(challs, user_id):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
    else:
        user_progress = list()
        user_data_str = dumps({'progress': user_progress}, indent=2)
        write_dp(user_id, user_data_str)

    for idx, c in challs.items():
        if idx in user_progress:
            c.is_completed = True

def load_data_from_csv(user_id):
    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    challs = dict()
    for c_idx, data in game_data.items():
        chall = Chall(data['idx'], data['name'], data['description'], data['answers'])
        challs[c_idx] = chall

    set_progress(challs, str(user_id))

    return challs

def get_options_keyboard(data, user_id, mode):
    if user_id not in data: data[user_id] = load_data_from_csv(user_id)
    challs = data[user_id]

    if mode == 'TRY':
        titles = [c.title for c in challs.values() if not c.is_completed]
        keys = [k for k, c in challs.items() if not c.is_completed]
    elif mode == 'SHOW':
        titles = [f'{c.title} ✅' if c.is_completed else c.title for c in challs.values()]
        keys = challs.keys()

    keyboard = [[InlineKeyboardButton(t, callback_data=k)] for t, k in zip(titles, keys)]

    return InlineKeyboardMarkup(keyboard)

def save_user_progress(user_id, context):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
    else:
        user_progress = list()

    user_progress.append(context.user_data['cur_chall_idx'])
    user_data_str = dumps({'progress': user_progress}, indent=2)
    write_dp(user_id, user_data_str)

def send_description(description, chat_id, bot):
    for d_filename in description:
        d_filename = path.join(DATA_DIR, d_filename)

        if d_filename.endswith('.jpg'):
            d_photo = open(d_filename, 'rb')
            bot_message = bot.send_photo(chat_id=chat_id, photo=d_photo)
        elif d_filename.endswith('.txt'):
            d_txt = open(d_filename).read()
            bot_message = bot.send_message(chat_id=chat_id, text=f'<code>{d_txt}</code>', parse_mode='HTML')
    
    return bot_message