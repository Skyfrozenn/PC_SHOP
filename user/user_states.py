from aiogram.fsm.state import StatesGroup,State


class Us(StatesGroup):
    wait_keyboard=State()
    wait_name=State()
    wait_age=State()
     