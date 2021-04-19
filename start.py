from aiogram import Bot, Dispatcher, executor, types
from aiogram import types
import aiogram.utils.markdown as fmt
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import logging
from aiogram.utils.exceptions import MessageNotModified
import asyncio
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime, timedelta
import db


bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    spends_type = State()

class Form2(StatesGroup):
    spends_write = State()


"""Main menu"""
@dp.message_handler(commands=["start"])
@dp.message_handler(Text(equals="Back"))
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Add spends", "Statistics"]
    keyboard.add(*buttons)
    chat_id = message.chat.id
    username = message.chat.username
    check_user = db.user_check(username, chat_id)
    await message.answer(f"<b>{check_user}</b>", reply_markup=keyboard,
                           parse_mode=types.ParseMode.HTML)


"""Add Spends menu"""
@dp.message_handler(Text(equals="Add spends"))
async def cmd_add_spends(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    spends = db.select_categories()
    buttons = ["Type", "Back"]
    lst = buttons + spends
    for item in lst:
        keyboard.add(item)
    spends_ = "\n".join(str(el) for el in spends)
    spends_clear = spends_.replace('(','').replace(')','').replace("'","")
    await message.answer(f"{spends}Please, choose one category.\nOr choose 'Type'", reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


"""Selected category"""
user_data = {}
@dp.message_handler(text=db.select_categories())
async def text_in_handler(message: types.Message):
    user_data[message.chat.username] = message.text
    category = message.text
    await Form2.spends_write.set()
    await message.answer(f"Please write amount for category:\n<b>{category}</b>",
                         parse_mode=types.ParseMode.HTML)

@dp.message_handler(state=Form2.spends_write)
async def cmd_write_spends(message: types.Message, state: FSMContext):
    username = message.chat.username
    spends = message.text
    category = user_data[message.chat.username]
    write = db.add_spend(username,category,spends)
    await state.finish()
    await message.answer(f"<u>Categoty: {category}\nSpends: {spends}</u>\n<b>{write}</b>", parse_mode=types.ParseMode.HTML)


"""Type spends"""
@dp.message_handler(Text(equals="Type"))
async def cmd_type_spends(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Cancel", "Back"]
    keyboard.add(*buttons)
    await Form.spends_type.set()
    await message.answer(f"Please type a spends\n<i>Examples:\nbar 800\nfood 1000</i>",
                         reply_markup=keyboard, parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(equals="Cancel"), state="*", )
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    #logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer("Cancelled")

@dp.message_handler(state=Form.spends_type)
async def cmd_type_spends(message: types.Message, state: FSMContext):
    username = message.chat.username
    message_raw = str(message.text)
    message_split = message_raw.split()
    amount = message_split[1]
    category = message_split[0]
    categories = db.select_categories()
    if category in categories:
        amount = float(message_split[1])
        write = db.add_spend(username,category,amount)
        await state.finish()
        await message.answer(f"<u>Categoty: {message_split[0]}\n"
                             f"Spends: {message_split[1]}</u>\n<b>{write}</b>",
                              parse_mode=types.ParseMode.HTML)
    else:
        await message.answer(f"{username} Please use existing categories!")


"""Statistics"""
@dp.message_handler(Text(equals="Statistics"))
async def cmd_statistics(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Daily", "Month", "Back", "Delete"]
    keyboard.add(*buttons)
    await message.answer("Statistics", reply_markup=keyboard)


@dp.message_handler(Text(equals="Daily"))
async def cmd_daily_stat(message: types.Message):
    stat = list()
    total = 0
    username = message.chat.username
    categories = db.select_categories()
    for category in categories:
        today_stat = db.get_today_statistics(username,category)
        if today_stat is None: continue
        else:
            total = total + today_stat
            newtup = (category, today_stat)
            stat.append(newtup)
    spends_ = "\n".join(str(el) for el in stat)
    spends_clear = spends_.replace('(','').replace(')','').replace("'","")
    await message.answer(f"<u>{spends_clear}</u>\n<b>Total\n{total}</b>", parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(equals="Month"))
async def cmd_month_stat(message: types.Message):
    username = message.chat.username
    categories = db.select_categories()
    stat = list()
    total = 0
    for category in categories:
        month_stat = db.get_month_statistics(username,category)
        if month_stat is None: continue
        else:
            total = total + month_stat
            newtup = (category, month_stat)
            stat.append(newtup)
    spends_ = "\n".join(str(el) for el in stat)
    spends_clear = spends_.replace('(','').replace(')','').replace("'","")
    await message.answer(f"<u>{spends_clear}</u>\n<b>Total\n{total}</b>", parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(equals="Delete spends"))
async def cmd_delete(message: types.Message):
    await message.answer("here list of categories from db\nChoose one to delete and type")

if __name__ == "__main__" :
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
