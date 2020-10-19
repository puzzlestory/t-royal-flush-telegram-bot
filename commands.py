from json import load, dump
from telegram.ext import ConversationHandler

CUR_RIGHT_ANSWER = ''
CHECK_ANSWER = range(1)

DATA_DIR = 'game_data/'
DATA_PATH = 'game_data/teste.json'

def show(update, context):
    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    challs = game_data.keys()
    update.message.reply_text('\n'.join(challs))

def try_to_answer(update, context):
    global CUR_RIGHT_ANSWER

    if not context.args:
        error_txt = 'Invalid input. Try with /try <chall_name>...'
        update.message.reply_text(error_txt)

        return ConversationHandler.END

    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    chall = ' '.join(context.args)
    if chall not in game_data.keys():
        error_txt = 'Challenge not found. Try again...'
        update.message.reply_text(error_txt)

        return ConversationHandler.END

    chat_id = update.message.chat_id
    for c_filename in game_data[chall]['content']:
        c_filename = f"{DATA_DIR}{c_filename}"

        if c_filename.endswith('.jpg'):
            context.bot.send_photo(chat_id=chat_id, photo=open(c_filename, 'rb'), caption=chall)
        elif c_filename.endswith('.txt'):
            c_file = open(c_filename)
            context.bot.send_message(chat_id=chat_id, text=c_file.read())

    intro_txt = 'Type your answer'
    update.message.reply_text(intro_txt)
    CUR_RIGHT_ANSWER = game_data[chall]['answer']

    return CHECK_ANSWER

def check_answer(update, context):
    global CUR_RIGHT_ANSWER

    answer = update.message.text
    if answer == CUR_RIGHT_ANSWER: result = 'Congratulations! You\'re right!'
    else: result = 'Oh no! Errooooou, seu burro!'

    CUR_RIGHT_ANSWER = ''
    update.message.reply_text(result)

    return ConversationHandler.END