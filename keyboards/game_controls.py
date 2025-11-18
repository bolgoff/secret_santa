from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def game_manage_kb(game_id: int, is_creator: bool):
    buttons = [
        [InlineKeyboardButton(text="👥 Участники", callback_data=f"game:players:{game_id}")],
        [InlineKeyboardButton(text="🔗 Ссылка", callback_data=f"game:link:{game_id}")],
    ]
    if is_creator:
        buttons.append([InlineKeyboardButton(text="🚫 Исключения", callback_data=f"game:excl_start:{game_id}")])
        buttons.append([InlineKeyboardButton(text="🎲 Жеребьевка", callback_data=f"game:draw:{game_id}")])
        buttons.append([InlineKeyboardButton(text="❌ Удалить игру", callback_data=f"game:delete:{game_id}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)