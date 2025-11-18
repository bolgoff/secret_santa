from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import requests as db
from keyboards.game_controls import game_manage_kb
from keyboards.main_menu import main_menu

router = Router()

@router.callback_query(F.data == "my_games")
async def list_games(callback: CallbackQuery):
    games = db.get_user_games(callback.from_user.id)
    if not games:
        await callback.answer("Нет активных игр", show_alert=True)
        return

    buttons = [[InlineKeyboardButton(text=g['name'], callback_data=f"game:view:{g['id']}")] for g in games]
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="main_menu")])
    
    await callback.message.edit_text("Ваши игры:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("game:view:"))
async def view_game(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[-1])
    game = db.get_game_by_id(game_id)
    
    is_creator = (game['creator_id'] == callback.from_user.id)
    text = f"🎅 {game['name']}\n💸 {game['budget']}\n📍 {game['location']}\n📅 {game['meeting_date']}"
    
    await callback.message.edit_text(text, reply_markup=game_manage_kb(game_id, is_creator), parse_mode="HTML")

@router.callback_query(F.data.startswith("game:players:"))
async def show_players(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[-1])
    players = db.get_players_in_game(game_id)
    
    txt = "\n".join([f"- {p['player_name']}" for p in players])
    game = db.get_game_by_id(game_id)
    is_creator = (game['creator_id'] == callback.from_user.id)
    
    await callback.message.edit_text(f"Участники:\n{txt}", reply_markup=game_manage_kb(game_id, is_creator))

@router.callback_query(F.data.startswith("game:link:"))
async def show_link(callback: CallbackQuery, bot: Bot):
    game_id = int(callback.data.split(":")[-1])
    game = db.get_game_by_id(game_id)
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={game['game_uuid']}"
    await callback.message.answer(f"Ссылка:\n{link}")
    await callback.answer()

@router.callback_query(F.data.startswith("game:delete:"))
async def delete_g(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[-1])
    db.delete_game(game_id)
    await callback.message.edit_text("Игра удалена.", reply_markup=main_menu())