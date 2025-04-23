from aiogram.utils.keyboard import ReplyKeyboardBuilder

def kb():
    builder=ReplyKeyboardBuilder()
    builder.button(text="Добавить Товар")
    builder.button(text="История Покупок пользователей")
    builder.button(text="Cписок доступных товаров")
    builder.button(text="Выйти")


    builder.adjust(2)
    repl_keyb = builder.as_markup(resize_keyboard=True)

    return repl_keyb 
