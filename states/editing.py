from aiogram.fsm.state import State, StatesGroup

class GameEditingSG(StatesGroup):
    waiting_new_wish = State()