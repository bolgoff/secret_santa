from aiogram.fsm.state import State, StatesGroup

class GameCreationSG(StatesGroup):
    name = State()
    budget = State()
    location = State()
    date = State()
    creator_name = State()
    creator_wish = State()