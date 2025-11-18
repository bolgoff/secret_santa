from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database import requests as db
from states.joining import GameJoiningSG
from keyboards.main_menu import main_menu
from utils import texts

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    user = message.from_user
    db.add_user(user.id, user.username, user.full_name)
    
    args = command.args
    if args:
        game = db.get_game_by_uuid(args)
        if not game:
            await message.answer(texts.ERR_NOT_FOUND)
            return
            
        if not game['is_active']:
            await message.answer(texts.ERR_GAME_STARTED)
            return

        existing = db.get_player(user.id, game['id'])
        if existing:
            await message.answer(texts.ERR_ALREADY_IN, reply_markup=main_menu())
            return

        await state.update_data(game_id=game['id'])
        await message.answer(f"Вступаем в игру <b>{game['name']}</b>.\nВведите ваше имя для игры:")
        await state.set_state(GameJoiningSG.name)
    else:
        await message.answer(texts.WELCOME, reply_markup=main_menu())

@router.callback_query(F.data == "main_menu")
async def back_home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(texts.WELCOME, reply_markup=main_menu())