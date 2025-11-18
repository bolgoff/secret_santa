from aiogram.fsm.state import State, StatesGroup

class GameJoiningSG(StatesGroup):
    name = State()
    wish = State()