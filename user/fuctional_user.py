from aiogram.types import Message,CallbackQuery
from aiogram.filters import CommandStart,Command
from aiogram import Router,F,Bot #импорт бота 
from aiogram.fsm.context import FSMContext
from .user_states import Us
from  bazed.data_baze import check_user,add_user
from .reply_user import us_kb,us_kb_too
from .inline_user import inline_keyb_user,inline_keyb_cart
from  bazed.data_baze  import input_tovars_users,input_tovars,check_us_product,user_by_tovar,cart_user,purchase_product,by_tovars_user,remove_from_cart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

user_rt=Router()


@user_rt.message(Command("user"))
async def user_reg(message:Message,state:FSMContext):
    us_id=message.from_user.id
    result=check_user(us_id)
    if result:
        await message.answer("Выберите действие-",reply_markup=us_kb())
        await state.set_state(Us.wait_keyboard)
    else:
        await message.answer("Чтобы пользоваться ботом нужно пройти регистрацию\nВведите Имя!")
        await state.set_state(Us.wait_name)

@user_rt.message(Us.wait_name)
async def save_name(message:Message,state:FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Имя сохранено,теперь введите свой возраст")
    await state.set_state(Us.wait_age)

@user_rt.message(Us.wait_age)
async def save_age(message:Message,state:FSMContext):
    user_id=message.from_user.id
    await state.update_data(age=message.text)
    users=await state.get_data()
    name=users.get("name")
    age=int(users.get("age"))
    await state.clear()
    add_user(name=name,age=age,user_id=user_id)
    await message.answer("Регистрация завершена,Выберите действие-",reply_markup=us_kb())
    await state.set_state(Us.wait_keyboard)


@user_rt.message(F.text == "Список товаров")
async def tovarss_us(message: Message, bot: Bot, state: FSMContext):
     
    result = input_tovars()  # Получаем все товары

     
    if result:
         
        for item in result:
            product_id = item.get("id")  # Получаем ID товара

            product_name = item.get("name_tovars")
            keyboard = inline_keyb_user(product_id=product_id, product_name=product_name)

            try:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=item["photo_tovars"],
                    caption=f"Название: {item['name_tovars']}\nЦена: {item['price']}\nКоличество на складе: {item['count']}",
                    reply_markup=keyboard
                )
            except Exception as e:
                await message.answer(f"Ошибка при отправке товара: {e}")
    else:
        print("tovarss_us: В result нет товаров")  # Добавляем отладочное сообщение
        await message.answer("Товаров нет")  # Если нет товаров выводим сообщение

    await state.set_state(Us.wait_keyboard)  # Устанавливаем состояние FSM


@user_rt.callback_query(F.data.startswith("product_"))
async def perform(query: CallbackQuery):
    tg_id = query.from_user.id
    product_id = int(query.data.split("_")[1])
    await query.answer("Выполнено")
     
    user_by_tovar(tg_id=tg_id,product_id=product_id)
    await query.message.answer("Товар добавлен в корзину")
    
          
     
@user_rt.message(F.text == "Корзина")
async def cart_us(message: Message, bot: Bot,state:FSMContext):

    user_id = message.from_user.id
    cart_items = cart_user(user_id)  # Получаем список товаров "в корзине"

    if cart_items:
        for item in cart_items:
            product_id = item["pr_id"]  # Исправлено: используем "pr_id" вместо "id"
            keyboard = inline_keyb_cart(product_id)  # Создаем inline-клавиатуру

            try:
                 
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=item["photo_tovars"],  # Исправлено: используем photo_tovars из item
                    caption=f"Ваши товары из корзины\nНазвание: {item['name_tovars']}\nЦена: {item['price']}\nКоличество на складе: {item["count"]}, количество в корзине : {item["quality"]}",  # Отображаем имя и цену
                    reply_markup=keyboard
                     
                )
                 
            except Exception as e:
                await message.answer(f"Ошибка при отправке товара: {e}")
    else:
        await message.answer("Ваша корзина пуста.")
    await state.set_state(Us.wait_keyboard)

 

    
     

     


     
@user_rt.callback_query(F.data.startswith('buy_'))
async def process_buy_callback(query: CallbackQuery,bot:Bot):
    user_id = query.from_user.id
    product_id = int(query.data.split('_')[1])

    if purchase_product(user_id, product_id):
        await query.answer("Товар успешно куплен!", show_alert=True)  # Уведомление
        await bot.delete_message(query.message.chat.id, query.message.message_id) #Удалим сообщение с товаром
        #TODO Сообщение об успешной покупке и список товаров в корзине
    else:
        await query.answer("Произошла ошибка при покупке товара.", show_alert=True)
    

@user_rt.message(F.text=="Выход")
async def exit(message:Message,state:FSMContext):
    await message.answer("Вы вышли из корзины товаров",reply_markup=us_kb())
    await state.set_state(Us.wait_keyboard)

@user_rt.message(F.text == "История ваших покупок")
async def by_tv(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    res = by_tovars_user(user_id=user_id)
    if res:
        tex = "Список Ваших купленных товаров:\n" # Исправлено: добавлено ":" в конце заголовка
        for item in res:
            tex += f"Имя товара:  ({item['name_tovars']})   -   Потрачено: {item['price']}\n"  # Исправлено форматирование текста
        await message.answer(tex) # Исправлено: используем message.answer для отправки текста
    else:
        await message.answer("Вы не купили ни одного товара.")  # Исправлено сообщение, если товаров нет

    await state.set_state(Us.wait_keyboard)



@user_rt.callback_query(F.data.startswith('del_'))
async def process_remove_from_cart_callback(query: CallbackQuery, bot: Bot):
    user_id = query.from_user.id
    product_id = int(query.data.split('_')[1])

    if remove_from_cart(user_id, product_id):
        await query.answer("Товар успешно удален из корзины!", show_alert=True)
        await bot.delete_message(query.message.chat.id, query.message.message_id)  # Уведомление
        # TODO: Обновить список товаров в корзине или удалить сообщение с товаром
    else:
        await query.answer("Произошла ошибка при удалении товара из корзины.", show_alert=True)