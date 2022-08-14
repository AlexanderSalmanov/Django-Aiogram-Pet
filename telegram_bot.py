from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from tg_bot.airtable_dump import table, airtable_record_filler

# from tg_bot.psql_loader import connect_to_postgres
from tg_bot.psql_loader import connect_to_postgres

import os
import dotenv

"""
    ------------ENVIRONMENT VARIABLE FETCHING PORTION------------------------
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

dotenv.read_dotenv()

token = os.environ.get('BOT_API_TOKEN')

import django
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()

"""

    -------------------BOT INITIALIZATION PORTION---------------------------

"""

bot = Bot(token=token)

dp = Dispatcher(bot, storage=MemoryStorage())

connect_to_postgres()

"""
    ----------KEYBOARD PORTION----------------
"""

b1 = KeyboardButton('/signup')
b2 = KeyboardButton('/help')


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_client.add(b1).insert(b2)

"""
    -----------DEFAULT START PORTION-----------
"""
@dp.message_handler(commands=['start', 'help'])
async def command_start(message : types.Message):
    await message.reply(
        'You are welcome to this little sneaky bot!\nIt allows simple user signup and submits data to Django back-end. Wonderful, isn\'t it? Select /signup option to get started!',
        reply_markup=kb_client)


"""
    ------------USER SIGNUP PORTION-------------
"""

class SignupForm(StatesGroup):
    username = State()
    email = State()
    password = State()

@dp.message_handler(commands='signup')
async def signup_start(message : types.Message):

    await SignupForm.username.set()
    await message.reply("Hello! You are now filling in your credentials.\nStart with your username.\nNOTE: You are always welcome to cancel this entire operation by typing `cancel`!")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message : types.Message, state : FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()

    await message.reply('Registration cancelled.')

@dp.message_handler(state=SignupForm.username)
async def process_username(message : types.Message, state : FSMContext):

    '''
    Username validation
    '''
    usernames = [item.username for item in users]

    if message.text in usernames:
        await message.reply(f"Username `{message.text}` is already taken.\nTry another username.")
        await state.reset(with_data=False)

    else:
        async with state.proxy() as data:
            data['username'] = message.text

        await SignupForm.next()
        await message.reply('Now type in your email')


@dp.message_handler(state=SignupForm.email)
async def process_email(message : types.Message, state : FSMContext):

    '''
    Email validation
    '''

    emails = [item.email for item in users]
    if message.text in emails:
        await message.reply(f"The email `{message.text}` is already taken.\nConsider trying something else.")
        await state.reset(with_data=False)
    else:
        async with state.proxy() as data:
            data['email'] = message.text

        await SignupForm.next()
        await message.reply('Lastly, type in your password.')

@dp.message_handler(state=SignupForm.password)
async def process_password(message : types.Message, state : FSMContext):


    '''
    Passwords validation
    '''

    passwords = [item.password for item in users]
    if message.text in passwords:
        await message.reply("This password is already used by someone else. Try some other one.")
        await state.reset(with_data=False)

    else:
        async with state.proxy() as data:
            data['password'] = message.text

            """
            This section fills Airtable 'Users' table with data entered during
            a single signup session
            """

            airtable_data = {
                'tg_id': str(message['from']['id']),
                'tg_username': message['from']['username'],
                'tg_fullname': f"{message['from']['first_name']} {message['from']['last_name']}",
                'username': data.get('username'),
                'email': data.get('email'),
                'password': data.get('password')
            }

            airtable_record_filler(table, **airtable_data)

            """
            This section creates Django 'auth_user' model with data entered during
            a single signup session
            """

            django_user_data = {key:value for key,value in airtable_data.items() if key in ['username', 'email', 'password']}

            User.objects.create_user(**django_user_data)

            login_link = 'https://django-tg-pet.herokuapp.com/login/'

            await message.reply(f'Registration successful.\nCredentials:\nLogin: <b>{data["username"]}</b>;\nPassword: <b>{data["password"]};</b>\nAuthorize <a href="{login_link}">here!</a>', parse_mode='HTML')
            await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
