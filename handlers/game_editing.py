from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import requests as db
from states.editing import GameEditingSG
from keyboards.game_controls import game_manage_kb
from keyboards.main_menu import main_menu

router = Router()

@router.callback_query(F.data.startswith("game:edit_wish:"))
async def edit_wish_start(callback: CallbackQuery, state: FSMContext):
    game_id = int(callback.data.split(":")[-1])
    
    player = db.get_player(callback.from_user.id, game_id)
    if not player:
        await callback.answer("Вы не в игре", show_alert=True)
        return

    await state.update_data(game_id=game_id, player_id=player['id'])
    
    text = (f"Ваше текущее пожелание:\n{player['wishlist']}\n\n"
            "Введите новое пожелание:")
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(GameEditingSG.waiting_new_wish)

@router.message(GameEditingSG.waiting_new_wish)
async def edit_wish_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    new_text = message.text
    
    db.update_wishlist(data['player_id'], new_text)
    
    await message.answer("✅ Пожелание обновлено!")
    await state.clear()
    
    game = db.get_game_by_id(data['game_id'])
    is_creator = (game['creator_id'] == message.from_user.id)
    
    text = f"🎅 {game['name']}\n💸 {game['budget']}\n📍 {game['location']}\n📅 {game['meeting_date']}"
    await message.answer(text, reply_markup=game_manage_kb(game['id'], is_creator), parse_mode="HTML")

@router.callback_query(F.data.startswith("game:leave:"))
async def leave_game_confirm(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[-1])
    game = db.get_game_by_id(game_id)
    
    if not game['is_active']:
        await callback.answer("Уже нельзя выйти!", show_alert=True)
        return

    if game['creator_id'] == callback.from_user.id:
        await callback.answer("Создатель не может выйти!", show_alert=True)
        return

    success = db.leave_game(game_id, callback.from_user.id)
    
    if success:
        await callback.message.edit_text(f"❌ Вы покинули игру {game['name']}. Пока, пока!", 
                                         reply_markup=main_menu(), 
                                         parse_mode="HTML")
    else:
        await callback.answer("Ошибка при выходе!", show_alert=True)