import uuid
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.creation import GameCreationSG
from database import requests as db
from keyboards.main_menu import main_menu

router = Router()

@router.callback_query(F.data == "create_game")
async def start_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название игры:")
    await state.set_state(GameCreationSG.name)
    await callback.answer()

@router.message(GameCreationSG.name)
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Бюджет подарка:")
    await state.set_state(GameCreationSG.budget)

@router.message(GameCreationSG.budget)
async def set_budget(msg: Message, state: FSMContext):
    await state.update_data(budget=msg.text)
    await msg.answer("Место встречи:")
    await state.set_state(GameCreationSG.location)

@router.message(GameCreationSG.location)
async def set_loc(msg: Message, state: FSMContext):
    await state.update_data(location=msg.text)
    await msg.answer("Дата встречи:")
    await state.set_state(GameCreationSG.date)

@router.message(GameCreationSG.date)
async def set_date(msg: Message, state: FSMContext):
    await state.update_data(date=msg.text)
    await msg.answer("Ваше имя в игре:")
    await state.set_state(GameCreationSG.creator_name)

@router.message(GameCreationSG.creator_name)
async def set_c_name(msg: Message, state: FSMContext):
    await state.update_data(creator_name=msg.text)
    await msg.answer("Ваше пожелание:")
    await state.set_state(GameCreationSG.creator_wish)

@router.message(GameCreationSG.creator_wish)
async def finish(msg: Message, state: FSMContext, bot):
    data = await state.get_data()
    new_uuid = str(uuid.uuid4())[:8]
    
    game_id = db.create_game(new_uuid, msg.from_user.id, data['name'], 
                             data['budget'], data['location'], data['date'])
    
    db.add_player(game_id, msg.from_user.id, data['creator_name'], msg.text)
    
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={new_uuid}"
    
    await msg.answer(f"Игра создана!\nСсылка: {link}", reply_markup=main_menu())
    await state.clear()