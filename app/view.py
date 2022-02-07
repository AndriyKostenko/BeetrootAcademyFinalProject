import logging
import urllib.request
import re
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, CommandHandler, Filters, Updater
from telegram.ext import CallbackQueryHandler
from datetime import date
from app import db, fapp
from config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NAME, SURNAME, AGE, HEIGHT, WEIGHT, PULSE, ARTERIAL_PRESSURE, PREFERABLE_SPORT, DATE = range(9)
RUNNING, PUSH_UPS, SIT_UPS = range(3)


# initializing the database
class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String)
    surname = db.Column(db.String)
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    pulse = db.Column(db.Integer)
    arterial_pressure = db.Column(db.Integer)
    preferable_sport = db.Column(db.String)
    date = db.Column(db.String)


# initializing the database
class Trainings(db.Model):
    __tablename__ = 'trainings'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.Integer, nullable=False)
    running = db.Column(db.Integer)
    push_ups = db.Column(db.Integer)
    sit_ups = db.Column(db.Integer)
    date = db.Column(db.Integer)


# starting the conversation for per.info
def add_info(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='1️⃣ Enter your name, please (ex. Andriy):', )
    return NAME


def name_handler(update: Update, context: CallbackContext):
    # receiving the name and teleg_id
    username = update.effective_message.text
    # validating username
    regex = re.compile(r"^[^\W0-9_]+([ \-'‧][^\W0-9_]+)*?$", re.U)
    res = regex.match(username)
    if not username or not res:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter correct username (ex. Andriy):')
        return NAME
    # temp. saving to the teleg. session
    context.user_data['username'] = username
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='2️⃣ Please, enter your surname (ex. Kostenko):')
    return SURNAME


def surname_handler(update: Update, context: CallbackContext):
    # receiving the surname
    surname = update.effective_message.text
    # validating
    regex = re.compile(r"^[^\W0-9_]+([ \-'‧][^\W0-9_]+)*?$", re.U)
    res = regex.match(surname)
    if not surname or not res:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct surname(ex. Kostenko):')
        return SURNAME
    context.user_data['surname'] = surname
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='3️⃣ Please, enter your age (ex. 27):', )
    return AGE


def age_handler(update: Update, context: CallbackContext):
    # receiving the age
    age = update.effective_message.text
    if not age or age == '0' or age.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct age (ex. 27):')
        return AGE
    context.user_data['age'] = age
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='4️⃣  Please, enter your height in cm. (ex. 175):', )
    return HEIGHT


def height_handler(update: Update, context: CallbackContext):
    # receiving the height
    height = update.effective_message.text
    if not height or height == '0' or height.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct height in cm. (ex. 175):')
        return HEIGHT
    context.user_data['height'] = height
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='5️⃣ Please, enter your weight in kgs (ex. 51):', )
    return WEIGHT


def weight_handler(update: Update, context: CallbackContext):
    weight = update.effective_message.text
    if not weight or weight == '0' or weight.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct weight in kgs. (ex. 50):')
        return WEIGHT
    context.user_data['weight'] = weight
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='6️⃣ Please, enter your current pulse (ex. 90):')
    return PULSE


def pulse_handler(update: Update, context: CallbackContext):
    # receiving the pulse
    pulse = update.effective_message.text
    if not pulse or pulse == '0' or pulse.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct pulse in digits (ex. 90):')
        return PULSE
    context.user_data['pulse'] = pulse
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='7️⃣ Please, enter your current arterial pressure (ex. 120/80):')
    return ARTERIAL_PRESSURE


def arterial_pressure_handler(update: Update, context: CallbackContext):
    # receiving the art.pressure
    arterial_pressure = update.effective_message.text
    regex = re.compile(r"(\d\d\d)[/](\d\d)")
    res = regex.match(arterial_pressure)
    if not arterial_pressure or not res:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct arterial pressure (ex. 120/80)!')
        return ARTERIAL_PRESSURE
    context.user_data['arterial_pressure'] = arterial_pressure
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='8️⃣ Please, enter your preferable sport (ex. football):')
    return PREFERABLE_SPORT


def finish_handler(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    preferable_sport = update.effective_message.text.lower()
    today = date.today()
    date_ = today.strftime("%d/%m/%Y")
    list_of_sports = ['nba', 'soccer', 'acrobatics', 'aerobic gymnastics', 'archery', 'arnis', 'artistic gymnastics',
                      'artistic swimming',
                      'badminton', 'baseball', 'basketball', 'baton twirling', 'bicycle motocross', 'billiards', 'pool',
                      'bobsleigh', 'bodybuilding', 'bowling', 'boxing', 'canoeing', 'car racing', 'cheerleading',
                      'chess', 'cricket', 'croquet', 'curling', 'dance sport', 'darts', 'diving', 'dodgeball',
                      'fencing',
                      'figure skating', 'football', 'frisbee', 'golf', 'handball', 'hang gliding', 'hockey',
                      'horseback riding', 'horse racing', 'ice hockey', 'ice skating', 'jet ski racing', 'judo',
                      'karate', 'kayaking', 'kendo', 'kick boxing', 'kite surfing', 'lacrosse', 'luge',
                      'mixed martial arts', 'motocross', 'muay thai', 'paintball', 'parachuting', 'paragliding',
                      'parkour', 'polo', 'pool/billiards', 'powerlifting', 'rafting', 'rhythmic gymnastics',
                      'rock climbing', 'rowing', 'rugby', 'sailing', 'sandboarding', 'scuba diving', 'shooting',
                      'skateboarding', 'skeleton', 'skiing', 'snowboarding', 'softball', 'speed skating',
                      'sport climbing', 'soccer', 'squash', 'sumo wrestling', 'surfing', 'swimming',
                      'synchronized skating', 'synchronized swimming', 'table tennis', 'taekwondo', 'tennis',
                      'track and field', 'trampolining', 'triathlon', 'tug of war', 'volleyball',
                      'water polo', 'weightlifting', 'windsurfing', 'wrestling', 'wu shu']
    if not preferable_sport or preferable_sport not in list_of_sports:
        update.message.reply_text(
            '⚠ Such sport is not found, please enter the correct preferable sport (ex. football): ')
        return PREFERABLE_SPORT

    context.user_data['telegram_user_id'] = telegram_user_id
    context.user_data['preferable_sport'] = preferable_sport
    context.user_data['date'] = date_

    user = Users.query.filter(Users.telegram_user_id == telegram_user_id).first()

    if not user:
        user = Users(telegram_user_id=context.user_data['telegram_user_id'], username=context.user_data['username'],
                     surname=context.user_data['surname'], age=context.user_data['age'],
                     height=context.user_data['height'], weight=context.user_data['weight'],
                     pulse=context.user_data['pulse'], arterial_pressure=context.user_data['arterial_pressure'],
                     preferable_sport=context.user_data['preferable_sport'], date=context.user_data['date'])
        db.session.add(user)
        db.session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='✔ Collecting the info has been completed.\n'
                                      '✔ You can return to /help info.')
        sticker = open('app/static/' + 'cat.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    else:
        user.username = context.user_data['username']
        user.surname = context.user_data['surname']
        user.age = context.user_data['age']
        user.height = context.user_data['height']
        user.weight = context.user_data['weight']
        user.pulse = context.user_data['pulse']
        user.arterial_pressure = context.user_data['arterial_pressure']
        user.preferable_sport = context.user_data['preferable_sport']
        user.date = context.user_data['date']
        db.session.add(user)
        db.session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='✔ Updating the info has been completed.\n'
                                      '✔ You can return to /help info.')
        sticker = open('app/static/' + 'cat.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    return ConversationHandler.END


def show_info(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    user = Users.query.filter(telegram_user_id == Users.telegram_user_id).first()
    if user:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'📄 Your info. 📄 \n'
                                      f'✔Name: {user.username}  {user.surname} \n'
                                      f'✔Age: {user.age} y.o.\n'
                                      f'✔Height: {user.height} cm.\n'
                                      f'✔Weight: {user.weight} kgs.\n'
                                      f'✔Last Pulse: {user.pulse} per/min.\n'
                                      f'✔Arterial pressure: {user.arterial_pressure} mmHg.\n'
                                      f'✔Main sport: {user.preferable_sport}.\n'
                                      f'✔Date of creation: {user.date}.')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='✖Sorry, no info.')


def remove_info(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    user = Users.query.filter(telegram_user_id == Users.telegram_user_id).first()
    if user is not None:
        Users.query.filter(telegram_user_id == Users.telegram_user_id).delete()
        db.session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='✔All your info successfully deleted!')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='✖Sorry, nothing to delete.')


def check_health_condition(update: Update, context: CallbackContext):
    telegram_user_id = update.message.from_user.id
    user = Users.query.filter(telegram_user_id == Users.telegram_user_id).first()

    if user:
        if user.height and user.weight and user.pulse and user.age and user.arterial_pressure:
            # weight_index_of_body = weight_kgs/(height_mtr^2)
            weight_index = "{:.3}".format((user.weight / ((user.height / 100) ** 2)))

            # physical_index = (700-(3*pulse)-(2.5*arterial_pressure)-(2.7*age)+(0.28*weight_kg)/
            # (350-(2.6*age)+(0.21*height_cm)) -0.5))
            # all other info are constants for thoose formula
            physical_index = "{:.3}".format((
                    (700 - (3 * user.pulse) - (2.5 * (eval(user.arterial_pressure))) - (2.7 * user.age)) /
                    (350 - (2.6 * user.age) + (0.21 * user.height)) - 0.5))

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"🏆 Health Condition Report 🏆\n"
                                          f"\nYour weight index: {weight_index}\n"
                                          f"⇨ ( 18-25 ) = 🥇 = good condition.\n"
                                          f"⇨ ( 16-18 ) = 🥈 = your weight is below normal.\n"
                                          f"⇨ ( 0-16 ) = 🥉 = you must to increase your weight.\n"
                                          f"⇨ ( 25-40 ) = 🥉 = overweight, you must to decrease your weight.\n"
                                          f"In generally:\n"
                                          f"The weight index means the correspondence between a person’s mass and his "
                                          f"height."
                                          f"It's evaluating whether the weight is insufficient, normal or excessive.\n"

                                          f"\n Your physical index: {physical_index}\n"
                                          f"⇨ ( index>0.825 ) = 🦸 !Superman! 🦸\n"
                                          f"⇨ ( 0.676-0.825 ) = 🥇 = above the average.\n"
                                          f"⇨ ( 0.526-0.676 ) = 🥈 = average.\n"
                                          f"⇨ ( index<0.526 ) = 🥉 = below average.\n"
                                          f"In generaly:\n"
                                          f"Physical index it is a complex of morphological, physical and functional "
                                          f"indicators"
                                          f"that shows the state of your body.If its value is below average, you "
                                          f"should do "
                                          f"health training and change your lifestyle towards a healthier one.\n ")

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="\n✖Not enough info. provided.\n"
                                          "Please check /show_info and update.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="\n✖Not enough info. provided.\n"
                                      "Please check /show_info and update.")


def plan_for_trainings(update: Update, context: CallbackContext):
    sticker = open('app/static/' + 'plan.webp', 'rb')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Hello, dear {update.effective_user.first_name}.\n'
                                  f'To make the plan for trainings,\n'
                                  f'i\'ll need to collect some data from you.\n'
                                  f'\n1️⃣ How many km. did you run this week?:')
    return RUNNING


def running_handler(update: Update, context: CallbackContext):
    running = update.effective_message.text
    if not running or running.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct running dist. (ex. 2):')
        return RUNNING

    context.user_data['running'] = running
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='2️⃣ How many push-ups did u make this week ? (ex. 100):')
    return PUSH_UPS


def push_ups_handler(update: Update, context: CallbackContext):
    push_ups = update.effective_message.text
    if not push_ups or push_ups.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct number of push-ups (ex. 50):')
        return PUSH_UPS
    context.user_data['push_ups'] = push_ups
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='✔ Info accepted.',
                             reply_markup=button_back_menu())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='3️⃣ How many sit-ups u did this week ? (ex. 100):')
    return SIT_UPS


def finish2_handler(update: Update, context: CallbackContext):
    weekly_running_norma = 5  # km
    weekly_push_ups_norma = 200  # times
    weekly_sit_ups_norma = 500  # times

    today = date.today()
    date_ = today.strftime("%d/%m/%Y")
    telegram_user_id = update.message.from_user.id

    sit_ups = update.effective_message.text
    if not sit_ups or sit_ups.isalpha():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='⚠ Please enter the correct number of sit-ups (ex. 50):')
        return SIT_UPS

    context.user_data['telegram_user_id'] = telegram_user_id
    context.user_data['sit_ups'] = sit_ups
    context.user_data['date'] = date_

    user = Trainings.query.filter(telegram_user_id == Trainings.telegram_user_id).first()
    if not user:
        user = Trainings(telegram_user_id=context.user_data['telegram_user_id'],
                         running=context.user_data['running'],
                         push_ups=context.user_data['push_ups'],
                         sit_ups=context.user_data['sit_ups'],
                         date=context.user_data['date'])
        db.session.add(user)
        db.session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'📄 Training plan info. 📄 \n'
                                      f'✔Remaining to run for this week: '
                                      f'{weekly_running_norma - user.running} km.\n'
                                      f'✔Remaining to push-up for this week: '
                                      f'{weekly_push_ups_norma - user.push_ups} times.\n'
                                      f'✔Remaining to sit-up for this week: '
                                      f'{weekly_sit_ups_norma - user.sit_ups} times.\n'
                                      f'✔Date of creation: {user.date}.\n'
                                      f'\n👍 General info: 👍\n'
                                      f'✏If you have minus, it means you are running forward of the base '
                                      f'programm.\n'
                                      f'✏Our base program for user consist of: 5 km of running, '
                                      f'200 push-ups and 500 sit-ups per week.')
        sticker = open('app/static/' + 'cat2.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    else:
        user.running = context.user_data['running']
        user.push_ups = context.user_data['push_ups']
        user.sit_ups = context.user_data['sit_ups']
        user.date = context.user_data['date']
        db.session.add(user)
        db.session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'📄 Training plan info. 📄 \n'
                                      f'✔Remaining to run for this week: '
                                      f'{weekly_running_norma - user.running} km.\n'
                                      f'✔Remaining to push-up for this week: '
                                      f'{weekly_push_ups_norma - user.push_ups} times.\n'
                                      f'✔Remaining to sit-up for this week: '
                                      f'{weekly_sit_ups_norma - user.sit_ups} times.\n'
                                      f'✔Date of creation: {user.date}.\n'
                                      f'\n👍 General info: 👍\n'
                                      f'✏If you have minus, it means you are running forward of the base '
                                      f'programm.\n'
                                      f'✏Our base program for user consist of: 5 km of running, '
                                      f'200 push-ups and 500 sit-ups per week.')
        sticker = open('app/static/' + 'cat2.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    return ConversationHandler.END


def motivate_yourself(update: Update, context: CallbackContext):
    random_search = random.randrange(0, 10)
    telegram_user_id = update.message.from_user.id
    user = Users.query.filter(telegram_user_id == Users.telegram_user_id).first()
    if user:
        if user.preferable_sport:
            searching_sport = user.preferable_sport
            searching_sport = searching_sport.replace(' ', '%')
            html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={searching_sport}")
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"https://www.youtube.com/watch?v={video_ids[random_search]}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="\n✖No user's preferable sport provided.\n")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="\n✖No user's info provided.\n")


def manage_text(update: Update, context: CallbackContext):
    msg = update.message.text.lower()

    if msg in ('hi', 'hello', 'hi bot', 'olla', 'holla'):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Hi, {update.effective_user.first_name}.\n"
                                      f"This is your personal sport-coach.\n"
                                      f"I'll assist you with improving of your health and body.\n"
                                      f"Press /help for more info.")
        sticker = open('app/static/' + 'sticker.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry, I can't understand you.\n"
                                      "Press /help for more info.")
        sticker2 = open('app/static/' + 'sticker2.webp', 'rb')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker2)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hi, {update.effective_user.first_name}.\n"
                                  f"This is your personal sport-coach.\n"
                                  f"I'll assist you with improving of your health and body.\n"
                                  f"Press /help for more info.")
    sticker = open('app/static/' + 'sticker.webp', 'rb')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    return ConversationHandler.END


def help_(update: Update, context: CallbackContext):
    sticker = open('app/static/' + 'help.webp', 'rb')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="\n📝 Things you can manage 📝\n"
                                  "- /add_or_update_info: to add/update personal info to the database.\n"
                                  "- /show_info:️to see personal info.\n"
                                  "- /remove_info: to remove all personal info from the database.\n"
                                  "\n‍🔥 Things you can check 🔥️\n"
                                  "- /check_health_condition: to check your current physical condition.\n"
                                  "- /plan_for_trainings: check the training plan.\n"
                                  "- /motivate_yourself: random videos for motivation")
    return ConversationHandler.END


def button_back_menu():
    button = [[InlineKeyboardButton('Cancel', callback_data='cancel')]]
    return InlineKeyboardMarkup(button)


def cancel_handler(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='⚠ Adding/updating info has been cancelled.\n'
                                  'To return to the main menu press /help.')
    return ConversationHandler.END


@fapp.route('/', methods=['GET', 'POST'])
def main():
    # Create the Updater
    updater = Updater(Config.TBOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # On different commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_))

    personal_data_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_or_update_info', add_info)],
        states={
            NAME: [MessageHandler(Filters.text & (~Filters.command), name_handler, pass_user_data=True)],
            SURNAME: [MessageHandler(Filters.text & (~Filters.command), surname_handler, pass_user_data=True)],
            AGE: [MessageHandler(Filters.text & (~Filters.command), age_handler, pass_user_data=True)],
            HEIGHT: [MessageHandler(Filters.text & (~Filters.command), height_handler, pass_user_data=True)],
            WEIGHT: [MessageHandler(Filters.text & (~Filters.command), weight_handler, pass_user_data=True)],
            PULSE: [MessageHandler(Filters.text & (~Filters.command), pulse_handler, pass_user_data=True)],
            ARTERIAL_PRESSURE: [
                MessageHandler(Filters.text & (~Filters.command), arterial_pressure_handler, pass_user_data=True)],
            PREFERABLE_SPORT: [
                MessageHandler(Filters.text & (~Filters.command), finish_handler, pass_user_data=True)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel_handler), CommandHandler('cancel', cancel_handler),
                   CallbackQueryHandler(cancel_handler, pattern='cancel'),
                   CommandHandler('start', start)],
        allow_reentry=True
    )

    trainings_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('plan_for_trainings', plan_for_trainings)],
        states={
            RUNNING: [MessageHandler(Filters.text & (~Filters.command), running_handler, pass_user_data=True), ],
            PUSH_UPS: [MessageHandler(Filters.text & (~Filters.command), push_ups_handler, pass_user_data=True), ],
            SIT_UPS: [MessageHandler(Filters.text & (~Filters.command), finish2_handler, pass_user_data=True), ],
        },
        fallbacks=[MessageHandler(Filters.command, cancel_handler), CommandHandler('cancel', cancel_handler),
                   CallbackQueryHandler(cancel_handler, pattern='cancel'),
                   CommandHandler('start', start)],
        allow_reentry=True
    )

    # SQL database
    dp.add_handler(personal_data_conv_handler)
    dp.add_handler(trainings_conv_handler)

    dp.add_handler(CommandHandler('add_or_update_info', add_info))
    dp.add_handler(CommandHandler('remove_info', remove_info))
    dp.add_handler(CommandHandler('show_info', show_info))
    dp.add_handler(CommandHandler('check_health_condition', check_health_condition))
    dp.add_handler(CommandHandler('plan_for_trainings', plan_for_trainings))
    dp.add_handler(CommandHandler('motivate_yourself', motivate_yourself))

    # On non-command, i.e just text message
    dp.add_handler(MessageHandler(Filters.text, manage_text))  # must be the last dispatcher

    # Start the Bot
    updater.start_polling()
    return "bot is working"
