from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from aiogram import Router,F,Bot #импорт бота 
from aiogram.fsm.context import FSMContext

from bazed.data_baze import add_tovars,input_tovars,get_all_users_bought_products # импорт с базы данных функции
from .keyb import kb # вот импорт 
from .states import Rep
from aiogram.types import ReplyKeyboardRemove


admin_rt=Router() 


@admin_rt.message(Command("admin"))
async def starting(message:Message,state:FSMContext):
    await message.answer("Выбери действие:",reply_markup=kb())
    await state.set_state(Rep.wait_keyboard) #Ожидание действия 

 
@admin_rt.message(F.text=="Добавить Товар")
async def add_tov(message:Message,state:FSMContext):
    await message.answer("Пришлите фотографию как будет выглядить ваш товар!")
    await state.set_state(Rep.photo_wait)


@admin_rt.message(Rep.photo_wait)
async def photo_tovarss(message:Message,state:FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    await message.answer("Фото сохранено! Теперь введимя имя товара")
    await state.set_state(Rep.name_wait)


@admin_rt.message(Rep.name_wait)
async def name_tovars(message:Message,state:FSMContext):
    name=message.text
    await state.update_data(name=name)
    await message.answer("Имя товара сохранено! Теперь введите цену товара")
    await state.set_state(Rep.price_wait)

@admin_rt.message(Rep.price_wait)
async def price_tovars(message:Message,state:FSMContext):
    price=message.text
    await state.update_data(price=price)
    await message.answer("С ценой разобрались,теперь укажите количества вашего товара ")
    await state.set_state(Rep.count_wait)


@admin_rt.message(Rep.count_wait)
async def save_tovars(message:Message,state:FSMContext):
    counts=message.text
    await state.update_data(counts=counts)
    tovars=await state.get_data()
    photo_tovars=tovars.get("photo")
    name_tovars=tovars.get("name")
    price=int(tovars.get("price"))
    count=int(tovars.get("counts"))
    print(f"Полученное количество: {counts}")
    add_tovars(photo_tovars=photo_tovars,name_tovars=name_tovars,price=price,count=count)
    await message.answer("Товар Добавлен!")
    await state.clear()
    await message.answer("Выбери действие:",reply_markup=kb())
    await state.set_state(Rep.wait_keyboard)


@admin_rt.message(F.text=="Выйти")
async def exit(message:Message):
    await message.answer("До скорых встреч!",reply_markup=ReplyKeyboardRemove())



@admin_rt.message(F.text == "Cписок доступных товаров")
async def inputs_pr(message: Message, bot: Bot,state:FSMContext):
    await message.answer("Выполнено!")
    result = input_tovars()

    if result is None:
        await message.answer("Товаров нет")
        return

    for item in result:
        try:
            # Отправляем фото
            await bot.send_photo(chat_id=message.chat.id, photo=item["photo_tovars"],
                                 caption=f"Название: {item['name_tovars']}\nЦена: {item['price']}\nКоличество на складе: {item['count']}")

        except Exception as e:
            await message.answer(f"Ошибка при отправке товара: {e}")
    await state.set_state(Rep.wait_keyboard)

@admin_rt.message(F.text=="История Покупок пользователей")
async def inp_tov_us(message:Message):
    result=get_all_users_bought_products()
    if result:
        text="Список покупок пользователей\n"
        for item in result:
            text+=f"Имя пользователя: {item["name"]}  - Товар:({item["tovars"]}) - Потратил:{item["price"]}\n\n"
        await message.answer(text)
    else:
        await message.answer("Покупок нет")

 
   