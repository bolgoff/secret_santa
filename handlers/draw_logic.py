from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import requests as db
from services.santa import match_players
from keyboards.game_controls import game_manage_kb
from keyboards.main_menu import main_menu

router = Router()

class ExclState(StatesGroup):
    giver = State()

@router.callback_query(F.data.startswith("game:excl_start:"))
async def excl_start(callback: CallbackQuery, state: FSMContext):
    game_id = int(callback.data.split(":")[-1])
    await state.update_data(game_id=game_id)
    
    players = db.get_players_in_game(game_id)
    kb = [[InlineKeyboardButton(text=f"От: {p['player_name']}", callback_data=f"excl:who:{p['id']}")] for p in players]
    kb.append([InlineKeyboardButton(text="Назад", callback_data=f"game:view:{game_id}")])
    
    await callback.message.edit_text("Выберите, КОМУ мы будем запрещать дарить:", 
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(ExclState.giver)

@router.callback_query(ExclState.giver, F.data.startswith("excl:who:"))
async def excl_who(callback: CallbackQuery, state: FSMContext):
    giver_id = int(callback.data.split(":")[-1])
    await state.update_data(giver_id=giver_id)
    
    data = await state.get_data()
    players = db.get_players_in_game(data['game_id'])
    
    kb = []
    for p in players:
        if p['id'] == giver_id: continue
        kb.append([InlineKeyboardButton(text=f"Не дарить: {p['player_name']}", callback_data=f"excl:done:{p['id']}")])
    
    await callback.message.edit_text("Кому этот игрок НЕ может дарить?", 
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(ExclState.giver, F.data.startswith("excl:done:"))
async def excl_done(callback: CallbackQuery, state: FSMContext):
    forbidden_id = int(callback.data.split(":")[-1])
    data = await state.get_data()
    
    db.add_exclusion(data['game_id'], data['giver_id'], forbidden_id)
    await callback.answer("Исключение добавлено")
    await state.clear()
    
    game = db.get_game_by_id(data['game_id'])
    await callback.message.edit_text(f"Меню игры {game['name']}", 
                                     reply_markup=game_manage_kb(data['game_id'], True))

@router.callback_query(F.data.startswith("game:draw:"))
async def run_draw(callback: CallbackQuery, bot: Bot):
    game_id = int(callback.data.split(":")[-1])
    players = db.get_players_in_game(game_id)
    
    if len(players) < 3:
        await callback.answer("Минимум 3 игрока!", show_alert=True)
        return
        
    exclusions = db.get_exclusions(game_id)
    p_ids = [p['id'] for p in players]
    
    matches = match_players(p_ids, exclusions)
    if not matches:
        await callback.answer("Ошибка! Невозможно составить пары.", show_alert=True)
        return
        
    db.deactivate_game(game_id)
    
    game = db.get_game_by_id(game_id)
    
    for giver_id, rec_id in matches.items():
        db.set_recipient(giver_id, rec_id)
        giver = db.get_player_by_id(giver_id)
        rec = db.get_player_by_id(rec_id)
        
        try:
            msg = f"🎅 <b>Жеребьевка!</b>\nВы дарите: <b>{rec['player_name']}</b>\nПожелание: {rec['wishlist']}\n\nБюджет: {game['budget']}"
            await bot.send_message(giver['user_id'], msg, parse_mode="HTML")
        except: pass
        
    await callback.message.edit_text("Жеребьевка проведена!", reply_markup=main_menu())