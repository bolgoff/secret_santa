from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Создать игру", callback_data="create_game")],
        [InlineKeyboardButton(text="📂 Мои игры", callback_data="my_games")]
    ])