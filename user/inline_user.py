# keyb.py (или где у вас находится inline_keyb_user)
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
 

def inline_keyb_user(product_id: int, product_name: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с кнопкой для одного товара.

    Args:
        product_id: ID товара.
        product_name: Название товара.

    Returns:
        InlineKeyboardMarkup: Объект aiogram InlineKeyboardMarkup.
    """
    builder = InlineKeyboardBuilder()
    button_text = f"Добавить в корзину: {product_name}"  # Формируем текст кнопки
    callback_data = f"product_{product_id}"  # Уникальные данные для callback

    builder.button(text=button_text, callback_data=callback_data)
    builder.adjust(1)  # Размещаем кнопку в один столбец
    return builder.as_markup()

def inline_keyb_cart(product_id): # функция клавиатура для вывода товаров из корзины
    """
    Создает inline-клавиатуру с кнопкой "Купить" для товара в корзине (с использованием InlineKeyboardBuilder).
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="Купить", callback_data=f"buy_{product_id}")
    builder.button(text="Удалить из корзины",callback_data=f"del_{product_id}")
    keyboard = builder.as_markup()
    return keyboard