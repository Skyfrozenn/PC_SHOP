from aiogram.fsm.state import StatesGroup,State


class Rep(StatesGroup):
    wait_keyboard=State()
    photo_wait=State()
    name_wait=State()
    price_wait=State()
    count_wait=State()