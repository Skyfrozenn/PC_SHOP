from sqlalchemy import create_engine,select,String,ForeignKey
from sqlalchemy.orm import Session,Mapped,mapped_column,sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base #создает подкобчения шаблон к бд
from sqlalchemy.exc import SQLAlchemyError



Base=declarative_base() # создает класс для таблицы и класса

engine=create_engine('sqlite:///users.db',echo=True) # подключения к бд

Session=sessionmaker(engine) # фабрика сессий для взаимодействия с бд

class User(Base):
    __tablename__="user"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]
    age:Mapped[int]
    user_id:Mapped[int]

    user_product:Mapped[list["Userproduct"]]=relationship(back_populates="user")
    def __repr__(self):  # Добавлен repr
        return f"<User(id={self.id}, name='{self.name}')>"
    
      



class Product(Base):
    __tablename__="product" 
    pr_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    photo_tovars:Mapped[str] 
    name_tovars:Mapped[str]
    price:Mapped[int]
    count:Mapped[int]

    product_user:Mapped[list["Userproduct"]]=relationship(back_populates="menu")
    def __repr__(self):  # Добавлен repr
        return f"<Product(pr_id={self.pr_id}, name_pr='{self.name_pr}')>"


class Userproduct(Base):
    __tablename__="user_product"
    id:Mapped[int]=mapped_column(autoincrement=True,primary_key=True)
    tg_id:Mapped[int]=mapped_column(ForeignKey(User.user_id)) # внешний ключ тг юзера
    product_id:Mapped[int]=mapped_column(ForeignKey(Product.pr_id)) # внеший ключ товара айди
    status:Mapped[str]=mapped_column(nullable=True) #статус в корзине или куплено
    quality:Mapped[int]=mapped_column(default=1) #количество +1 или создавать

    user:Mapped["User"]=relationship(back_populates="user_product") # связь с классом Юзер
    menu:Mapped["Product"]=relationship(back_populates="product_user") # связь с классом товаров 
    def __repr__(self):  # Добавлен repr
        return f"<Userproduct(user_id={self.user_id}, product_id={self.product_id}, status='{self.status}')>"
    
Base.metadata.create_all(engine)





def add_tovars(photo_tovars,name_tovars,price,count):  #добавление товара (АДМИНУ) и проверка есть ли товар 
    with Session.begin() as session:
            new_tovars=Product(photo_tovars=photo_tovars,name_tovars=name_tovars,price=price,count=count)
            session.add(new_tovars)
         

    
def input_tovars():
    with Session() as sesion: #список всех товаров для админа
        tovars = sesion.scalars(select(Product).where(Product.count > 0)).all() #фильтруем товары count > 0
        if tovars:
            print("input_tovars: Товары найдены в базе данных") #Добавляем отладочное сообщение
            result = []  # Создаем список для хранения результатов
            for obj in tovars:
                result.append({
                    "id":obj.pr_id,
                    "photo_tovars": obj.photo_tovars,
                    "name_tovars": obj.name_tovars,
                    "price": obj.price,
                    "count": obj.count
                })
            return result
        else:
            print("input_tovars: Товары не найдены в базе данных") #Добавляем отладочное сообщение
            return None# Возвращаем None если товаров нет
        
def check_user(tg_id): # проверяет существует ли пользователь 
    with Session() as session:
        stmt = select(User).where(User.user_id == tg_id)
        user = session.scalar(stmt)
        if user is not None:
            return True
        else:
            return False
 

 
        

def add_user(name,age,user_id): #добавляем пользователя 
    with Session.begin() as sesion:
        new_users=User(name=name,age=age,user_id=user_id)
        sesion.add(new_users)


def input_tovars_users(): # список товаров для юзера в инлайн клавиатуру 
    with Session() as sesion:  
        tovars = sesion.scalars(select(Product).where(Product.count > 0)).all()
        if tovars:
            result = []  # Создаем список для хранения результатов
            for obj in tovars:
                result.append({
                    "pr_id":obj.pr_id,
                    "name_tovars": obj.name_tovars
                })
            return result
        else:
            return None # Возвращаем None если товаров нет

 

def check_us_product(pr_id,user_id): #проверка есть ли товар в промежуточной таблцце
    with Session() as sesion:
        stml=sesion.scalar(select(Userproduct).where(Userproduct.product_id==pr_id,Userproduct.tg_id==user_id))
        if stml is not None:
            return True
        else:
            return False

def user_by_tovar(tg_id: int, product_id: int):  # добавляет товар и юзера в промежут таблицу со статусом в корзине
    """Добавляет товар и юзера в промежуточную таблицу со статусом в корзине.

    Если запись уже существует, увеличивает quality на 1.
    Если записи нет, создает новую запись с quality = 1 (по умолчанию).
    """
    try:
        with Session.begin() as session:
            user = session.scalar(select(User).where(User.user_id == tg_id))
            product = session.scalar(select(Product).where(Product.pr_id == product_id))

            if not user or not product:
                print("Товар или пользователь отсутствует")
                return  # Или выбросить исключение, в зависимости от логики

            # Проверяем, есть ли запись в промежуточной таблице
            existing_user_product = session.scalar(
                select(Userproduct)
                .where(Userproduct.tg_id == user.user_id)
                .where(Userproduct.product_id == product.pr_id)
            )

            if existing_user_product:
                # Увеличиваем quality
                existing_user_product.quality += 1
                print("Запись в промежуточной таблице найдена, quality увеличено")
            else:
                # Создаем новую запись
                new_user_product = Userproduct(tg_id=user.user_id, product_id=product.pr_id, status="В корзине")  # quality по умолчанию = 1
                session.add(new_user_product)
                print("Новая запись в промежуточной таблице создана")
            session.commit()
            print("Транзакция успешно завершена")

    except SQLAlchemyError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        session.rollback()  # Автоматически делается при with session.begin()
        raise  # Пробросить исключение наверх, чтобы обработать в вызывающем коде
 

    
def cart_user(user_id):  # вывод всех товаров юзера со статусом "в корзине"
    with Session() as session:
        user_products = session.scalars(
            select(Userproduct)
            .where(Userproduct.quality > 0, Userproduct.tg_id == user_id, Userproduct.status == "В корзине")
        ).all()

        if user_products:
            cart_items = []
            for user_product in user_products:
                if user_product.menu.count > 0:
                    cart_items.append({
                        "photo_tovars": user_product.menu.photo_tovars,
                        "pr_id": user_product.menu.pr_id,
                        "name_tovars": user_product.menu.name_tovars,
                        "price": user_product.menu.price,
                        "count": user_product.menu.count,
                        "quality":user_product.quality

                    })
                else:
                    continue
            return cart_items  # <--- Перемещено за пределы цикла
        else:
            return None  # Возвращаем None, если товаров в корзине нет


 

def purchase_product(tg_id: int, product_id: int):
    """Добавляет товар в список купленных товаров для пользователя и уменьшает количество товара.

    Если запись уже существует со статусом "Куплено", увеличивает quality на 1.
    Если записи нет, создает новую запись со статусом "Куплено" и quality = 1 (по умолчанию).
    Также уменьшает количество товара в таблице Product на 1.
    """
    try:
        with Session.begin() as session:
            user = session.scalar(select(User).where(User.user_id == tg_id))
            product = session.scalar(select(Product).where(Product.pr_id == product_id))

            if not user or not product:
                print("Товар или пользователь отсутствует")
                return False  # Или выбросить исключение, в зависимости от логики

            # 1. Проверяем, есть ли запись в промежуточной таблице со статусом "Куплено"
            existing_user_product = session.scalar(
                select(Userproduct)
                .where(Userproduct.tg_id == user.user_id)
                .where(Userproduct.product_id == product.pr_id)
                .where(Userproduct.status == "Куплено")
            )

            if existing_user_product:
                # Увеличиваем quality
                existing_user_product.quality += 1
                print("Запись со статусом 'Куплено' найдена, quality увеличено")
            else:
                # Создаем новую запись
                new_user_product = Userproduct(tg_id=user.user_id, product_id=product.pr_id, status="Куплено")  # quality по умолчанию = 1
                session.add(new_user_product)
                print("Новая запись со статусом 'Куплено' создана")

            # 2. Уменьшаем количество товара в таблице Product
            product.count -= 1
            session.add(product) # Явно обновляем запись в БД, т.к. мы её меняем

            session.commit()
            print("Транзакция успешно завершена")
            return True #Успех

    except SQLAlchemyError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        session.rollback()
        return False #Ошибка
    except SQLAlchemyError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        session.rollback()  # Автоматически делается при with session.begin()
        raise  # Пробросить исключение наверх, чтобы обработать в вызывающем коде

def by_tovars_user(user_id): #купленые товары юзера
    with Session() as sesion:
        user_tovar=sesion.scalars(select(Userproduct).where(Userproduct.tg_id==user_id,Userproduct.status == "Куплено" ))
        if user_tovar:
            tovars=[]
            
            for obj in user_tovar:
                tovars.append({
                    "id":obj.menu.pr_id,
                    "name_tovars":obj.menu.name_tovars,
                    "price":obj.menu.price

                })
            return tovars
        else:
            return False
        
def get_all_users_bought_products():
    with Session() as sesion:
        us_tv=sesion.scalars(select(Userproduct).where(Userproduct.status == "Куплено"))
        if us_tv:
            res=[]
            for item in us_tv:
                res.append({
                    "name":item.user.name,
                    "tovars":item.menu.name_tovars,
                    "price":item.menu.price
                })
            return res
        else:
            return "Товаров нет"
  
     
         
def remove_from_cart(tg_id: int, product_id: int):
    """Удаляет товар из корзины пользователя или уменьшает quantity на 1.

    Если quantity становится равным 0, удаляет запись из промежуточной таблицы.
    """
    try:
        with Session.begin() as session:
            # 1. Находим запись в промежуточной таблице для данного пользователя и товара
            user_product = session.scalar(
                select(Userproduct)
                .where(Userproduct.tg_id == tg_id)
                .where(Userproduct.product_id == product_id)
                .where(Userproduct.status == "В корзине")  # <--- Важно указать статус "В корзине"
            )

            if not user_product:
                print("Товар не найден в корзине пользователя")
                return False  # Товар не найден

            # 2. Уменьшаем quantity
            user_product.quality -= 1

            if user_product.quality > 0:
                # 3a. Если quantity больше 0, обновляем запись
                session.add(user_product)  # Явное добавление для обновления
                print("Quantity товара в корзине уменьшено")
            else:
                # 3b. Если quantity равно 0, удаляем запись
                session.delete(user_product)
                print("Товар удален из корзины")

            session.commit()
            print("Транзакция успешно завершена")
            return True

    except SQLAlchemyError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        session.rollback()
        raise  # Пробросить ошибку