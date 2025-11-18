from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.joining import GameJoiningSG
from database import requests as db
from keyboards.main_menu import main_menu
from utils import texts

router = Router()

@router.message(GameJoiningSG.name)
async def join_name(msg: Message, state: FSMContext):
    await state.update_data(player_name=msg.text)
    await msg.answer("Пожелание:")
    await state.set_state(GameJoiningSG.wish)

@router.message(GameJoiningSG.wish)
async def join_wish(msg: Message, state: FSMContext, bot):
    data = await state.get_data()
    game_id = data['game_id']
    
    db.add_player(game_id, msg.from_user.id, data['player_name'], msg.text)
    
    # Уведомляем создателя
    game = db.get_game_by_id(game_id)
    try:
        await bot.send_message(game['creator_id'], f"👋 Новый игрок в '{game['name']}': {data['player_name']}")
    except: pass

    await msg.answer(texts.SUCCESS_JOIN, reply_markup=main_menu())
    await state.clear()