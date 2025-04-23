from aiogram.utils.keyboard import ReplyKeyboardBuilder

def us_kb():
    builder=ReplyKeyboardBuilder()
    builder.button(text="Список товаров")
    builder.button(text="Корзина")
    builder.button(text="История ваших покупок")
    builder.button(text="Выйти")


    builder.adjust(2)
    us_keyb = builder.as_markup(resize_keyboard=True)

    return us_keyb



def us_kb_too():
    builder=ReplyKeyboardBuilder()
    builder.button(text="Купить товар")
    builder.button(text="Выход")
    builder.adjust(2)
    us_keyb_too=builder.as_markup(resize_keyboard=True)
    return us_keyb_too

