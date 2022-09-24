from telebot import TeleBot
from telebot.types import Message
from telebot import types
from buttons import BuildButtons
from messages import Messages
from models import (Customer, 
                    Basket, 
                    Product, 
                    Order,
                    ProductOrder)
from config import (CURRENCY, TOKEN, DB_FILENAME,
                    CALLBACK_CHAT_NOTIFICATION)
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker              
from filters import (in_basket_product_id, buy_product_id,
                    minus_product_id, plus_product_id,
                    delete_product_id, add_product_admin,
                    remove_product_admin, change_count_product_admin,
                    change_desc_product_admin, change_title_product_admin,
                    change_price_product_admin, pay_order_admin,
                    plus_price_order_admin, change_price_order_admin)
from sqlalchemy import text
import datetime

msg = Messages()
btn = BuildButtons()

engine = create_engine(f'sqlite:///{DB_FILENAME}')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_image_id(message: Message, bot: TeleBot):
    '''
    Получение ID изображения.
    Только для админов.
    '''
    def fuc_get_image_id(message: Message):
        if not message.photo:
            return
        bot.send_message(message.chat.id, message.photo[-1].file_id)
    back_mag = bot.send_message(message.chat.id, msg['get_image'], parse_mode='markdown')
    bot.register_next_step_handler(back_mag, fuc_get_image_id)


def get_me(message: Message, bot: TeleBot):
    '''
    Получить информацию о себе
    '''
    first_name = msg['first_name']
    last_name = msg['last_name']
    chat = msg['chat']
    me = f'*ID:* {message.from_user.id}\n\
*{chat}:* {message.chat.id}\n\
*{first_name}:* {message.from_user.first_name}\n\
*{last_name}:* {message.from_user.last_name}'
    bot.send_message(message.chat.id, me, parse_mode='markdown')


def shop_user(message: Message, bot: TeleBot):
    '''
    Запуск при входе - для пользователя
    '''
    wellcom = msg['wellcom'] % (message.from_user.first_name,)
    bot.send_message(message.chat.id, wellcom, reply_markup=btn.main_menu_user())


def shop_admin(message: Message, bot: TeleBot):
    '''
    Запуск при входе в бота - для админов
    '''
    wellcom = msg['wellcom'] % (message.from_user.first_name,)
    bot.send_message(message.chat.id, wellcom, reply_markup=btn.main_menu_admin())


def admin_panel(message: Message, bot: TeleBot):
    '''
    Запуск при нажатие кнопки - Админ панель
    '''
    wellcom = msg['wellcom_admin'] % (message.from_user.first_name,)
    bot.send_message(message.chat.id, wellcom, reply_markup=btn.admin_panel())


def shop_list_product(message: Message, bot: TeleBot):
    '''
    Вывод товаров из БД для покупки
    '''
    with Session() as session:
        query = session.query(Product).filter(Product.is_active).all()
    if not query:
        return bot.send_message(message.chat.id, msg['no_products'])

    for product in query:
        price = '*{}:* {} {}'.format(str(msg['price']), product.price, product.currency)
        grand = '*{}:* {} {}'.format(msg['in_stock'], product.quantity, msg['grand'])
        bot.send_photo(message.chat.id, 
                    photo=product.photo,
                    caption=f'*{product.title}*\n{price}\n{grand}\n\n{product.description}',
                    parse_mode='markdown',
                    reply_markup=btn.panel_under_product(product.id))


def func_add_in_basket(call: types.CallbackQuery, bot: TeleBot, data: dict):
    '''
    Функция для добавления товара в корзину. 
    '''
    product_id = data.get('id')
    with Session() as session:
        # product = session.query(Product).filter_by(is_active=True, id=data.get('id')).first()
        customer = session.query(Customer).filter_by(user_id=call.from_user.id).first()
        if not customer:
            session.add(
                Customer(
                    user_id = call.from_user.id,
                    first_name = call.from_user.first_name,
                    last_name = call.from_user.last_name
                )
            )
            session.commit()
            customer = session.query(Customer).filter_by(user_id=call.from_user.id).first()
        item_basket = session.query(Basket).filter_by(product_id=product_id, customer_id=customer.id).first()
        if not item_basket:
            session.add(
                Basket(
                    customer_id = customer.id,
                    product_id = product_id,
                    quantity = 1
                )
            )
        else:
            session.query(Basket).filter_by(product_id=product_id, customer_id=customer.id).update(
                {
                    Basket.quantity: Basket.quantity + 1
                }
            )
        session.commit()

def add_in_basket(call: types.CallbackQuery, bot: TeleBot):
    '''
    Положить товар в корзину
    data: dict = {'@': 'in_basket_product_id', 'id': '1'}
    '''
    data: dict = in_basket_product_id.parse(callback_data=call.data)
    func_add_in_basket(call, bot, data)
    
    bot.send_message(call.from_user.id, msg['add_product'])


def get_itog(message: Message, bot: TeleBot):
    '''
    Получает сумму всех товаров в корзине пользователя
    '''
    with Session() as session:
        query = '''
            SELECT product.currency, sum(basket.quantity*product.price) as amount
            FROM basket
            JOIN customer ON customer.id = basket.customer_id
            JOIN product ON product.id = basket.product_id
            WHERE customer.user_id = :user_id
            GROUP BY product.currency
        '''
        records = session.execute(query, {'user_id':message.chat.id,})
        record = records.mappings().first()
        return record.amount

def get_itog_sum(message: Message, bot: TeleBot):
    '''
    Получает сумму всех товаров в корзине пользователя и отправляет ответ
    '''
    with Session() as session:
        query = '''
            SELECT product.currency, sum(basket.quantity*product.price) as amount
            FROM basket
            JOIN customer ON customer.id = basket.customer_id
            JOIN product ON product.id = basket.product_id
            WHERE customer.user_id = :user_id
            GROUP BY product.currency
        '''
        records = session.execute(query, {'user_id':message.chat.id,})
        list_record = records.mappings().all()
    all_sum = 0
    tmp_currency = CURRENCY
    if not list_record:
        itog = '*{}:* {} {}'.format(msg['itog'], all_sum, tmp_currency)
        bot.send_message(message.chat.id, itog,
                        parse_mode='markdown')
    for item in list_record:
        all_sum = item.get('amount')
        tmp_currency = item.get('currency')
        itog = '*{}:* {} {}'.format(msg['itog'], all_sum, tmp_currency)
        bot.send_message(message.chat.id, itog,
                        parse_mode='markdown')
        


def list_in_basket(message: Message, bot: TeleBot):
    '''
    Список товаров в корзине
    '''
    with Session() as session:
        query = session.query(Basket).join(Customer, Basket.customer_id==Customer.id)\
                                                .filter_by(user_id=message.from_user.id)
        if not query.count():
            return bot.send_message(message.chat.id, msg['clear_basket'])

        for item_basket in query:
            sum = '*{}:* {} {}'.format(str(msg['sum']), \
                item_basket.product.price*item_basket.quantity, item_basket.product.currency)
            quantity = '*{}:* {} {}'.format(msg['quantity'], item_basket.quantity, msg['grand'])
            bot.send_photo(message.chat.id, 
                    photo=item_basket.product.photo,
                    caption=f'*{item_basket.product.title}*\n{sum}\n{quantity}',
                    parse_mode='markdown',
                    reply_markup=btn.panel_product_basket(item_basket.product.id))
        get_itog_sum(message, bot)


def add_product_in_basket(call: types.CallbackQuery, bot: TeleBot):
    '''
    Добавляет товар в корзину пользователя.
    '''
    data: dict = plus_product_id.parse(callback_data=call.data)
    product_id = data.get('id')
    with Session() as session:
        product_basket = session.query(Basket).filter_by(product_id=product_id)\
                                                .join(Customer, Customer.id==Basket.customer_id)\
                                                .filter_by(user_id=call.from_user.id).first()
        if not product_basket:
            return bot.send_message(call.message.chat.id, msg['no_product_basket'])
        query = '''
            UPDATE basket
            SET quantity = quantity + 1
            WHERE basket.product_id = :productid
                AND basket.customer_id IN (
                    SELECT customer.id
                    FROM customer
                    WHERE customer.user_id = :userid
                )
        '''
        session.execute(text(query), {'productid':product_id, 'userid': call.message.chat.id})
        session.commit()

        
        sum = '*{}:* {} {}'.format(str(msg['sum']), \
                product_basket.product.price*product_basket.quantity, product_basket.product.currency)
        quantity = '*{}:* {} {}'.format(msg['quantity'], product_basket.quantity, msg['grand'])
        bot.edit_message_caption(caption=f'*{product_basket.product.title}*\n{sum}\n{quantity}',\
                                chat_id=call.message.chat.id, 
                                message_id=call.message.message_id,
                                parse_mode='markdown',
                                reply_markup=btn.panel_product_basket(product_basket.product.id))
        get_itog_sum(call.message, bot)


def minus_product_in_basket(call: types.CallbackQuery, bot: TeleBot):
    '''
    Уменьшает товар в корзине пользователя.
    '''
    data: dict = minus_product_id.parse(callback_data=call.data)
    product_id = data.get('id')
    with Session() as session:
        prod = session.query(Basket).filter_by(product_id=product_id)\
                                    .join(Customer, Customer.id==Basket.customer_id)\
                                    .filter_by(user_id=call.from_user.id).first()
        if not prod:
            return bot.send_message(call.message.chat.id, msg['no_product_basket'])                            
        if prod.quantity > 1:
            query = '''
            UPDATE basket
            SET quantity = quantity - 1
            WHERE basket.product_id = :productid
                AND basket.customer_id IN (
                    SELECT customer.id
                    FROM customer
                    WHERE customer.user_id = :userid
                )
            '''
            session.execute(text(query), {'productid':product_id, 'userid': call.message.chat.id})
            session.commit()

            product_basket = session.query(Basket).filter_by(product_id=product_id)\
                                                .join(Customer, Customer.id==Basket.customer_id)\
                                                .filter_by(user_id=call.from_user.id).first()
            sum = '*{}:* {} {}'.format(str(msg['sum']), \
                    product_basket.product.price*product_basket.quantity, product_basket.product.currency)
            quantity = '*{}:* {} {}'.format(msg['quantity'], product_basket.quantity, msg['grand'])
            bot.edit_message_caption(caption=f'*{product_basket.product.title}*\n{sum}\n{quantity}',\
                                    chat_id=call.message.chat.id, 
                                    message_id=call.message.message_id,
                                    parse_mode='markdown',
                                    reply_markup=btn.panel_product_basket(product_basket.product.id))
            get_itog_sum(call.message, bot)


def delete_product_in_basket(call: types.CallbackQuery, bot: TeleBot):
    '''
    Удаляет товар из корзины пользователя
    '''
    data: dict = delete_product_id.parse(callback_data=call.data)
    product_id = data.get('id')
    with Session() as session:
        product_basket = session.query(Basket).filter_by(product_id=product_id)\
                                    .join(Customer, Customer.id==Basket.customer_id)\
                                    .filter_by(user_id=call.from_user.id).first()
        if not product_basket:
            return bot.send_message(call.message.chat.id, msg['no_product_basket'])
        query = '''
            DELETE FROM basket
            WHERE basket.product_id = :productid
                AND basket.customer_id IN (
                    SELECT customer.id
                    FROM customer
                    WHERE customer.user_id = :userid
                )
        '''
        session.execute(text(query), {'productid':product_id, 'userid': call.message.chat.id})
        session.commit()
        bot.edit_message_caption(caption=msg['delete_product'], chat_id=call.message.chat.id, \
                                message_id=call.message.message_id)
        get_itog_sum(call.message, bot)


def add_product_order(message: Message, bot: TeleBot):
    '''
    Добавление кнопок для завершения оформления заказа
    '''
    with Session() as session:
        record = session.query(Basket).join(Customer, Customer.id==Basket.customer_id)\
                                    .filter_by(user_id=message.from_user.id).first()
        if not record:                            
            return bot.send_message(message.chat.id, msg['no_order'])
            
        bot.send_message(message.chat.id, msg['request_order'], reply_markup=btn.panel_add_order())


def create_check_oredr(products, itog, orderid, date):
    '''
    Формирование товарного чека для потребителя
    '''
    check_str = '*{} №{}* 🧾\n\n'.format(msg['check_head'], orderid, date.strftime('%d-%m-%Y %H:%M'))
    check_str += '*{}* | *{}* | *{}* | *{}*\n'.format(msg['product'],
                                                msg['price'],
                                                msg['quantity'],
                                                msg['sum'])
    for product in products:
        check_str += '{}  {} {}  x{}  {} {}\n'.format(product.product.title,
                                            product.product.price,
                                            product.product.currency,
                                            product.quantity,
                                            product.quantity * product.product.price,
                                            product.product.currency)
    check_str += '\n*{}:* {} {}'.format(msg['itog'], itog, CURRENCY)
    return check_str

def callback_notification_admin(bot: TeleBot, order_id):
    '''
    Отправления уведомлений для админа о новом заказе
    '''
    for chat in CALLBACK_CHAT_NOTIFICATION:
        bot.send_message(chat, msg['new_order_shop']+' {} №{} 🧾'.format(msg['product_check'], order_id))

def send_my_contact(message: Message, bot: TeleBot):
    '''
    Создание заказа. Отправка чека потребителю. Отправка уведомления о заказе.
    '''
    with Session() as session:
        user = session.query(Customer).filter_by(user_id=message.contact.user_id).first()
        if not user:
            session.query(Customer).filter_by(user_id=message.contact.user_id)\
                                    .update({
                                        Customer.phone_number: message.contact.phone_number
                                    })
            session.commit()
        if user:
            amount = get_itog(message, bot)
            order_user = Order(
                customer = user,
                amount = amount
            )
            items_basket = session.query(Basket).filter_by(customer=user).all()
            for item_basket in items_basket:
                p = ProductOrder(
                    order_id = order_user.id,
                    product_id = item_basket.id,
                    currency = item_basket.product.currency,
                    quantity = item_basket.quantity,
                    amount = item_basket.quantity * item_basket.product.price
                )
                order_user.products.append(p)

            session.add_all([order_user,])
            session.commit()

            check = create_check_oredr(items_basket, amount, order_user.id, order_user.date)

            session.query(Basket).filter_by(customer=user).delete()
            session.commit()

            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, msg['success_contact'])
            bot.send_message(message.chat.id, check, parse_mode='markdown')
            callback_notification_admin(bot, order_user.id)
        else:
            bot.send_message(message.chat.id, msg['no_search_user'])


def customer_in_admin(message: Message, bot: TeleBot):
    '''
    Вывод списка покупателей в админке
    '''
    with Session() as session:
        user_query = session.query(Customer).order_by(Customer.last_name)
        str_customer = '*{}*\n\n'.format(msg['customers'])
        str_customer += '*{}* | *{}* | *{}* | *{}*\n'\
            .format('ID',msg['last_name'], msg['first_name'],msg['phone_number'])
        list_customer = ''
        for user in user_query:
            list_customer += '\n-----------------------------------------\n'
            list_customer += '`{}` {} {} `{}`'.format(user.user_id,
                                                user.last_name,
                                                user.first_name,
                                                user.phone_number)
        if not list_customer:
            return bot.send_message(message.chat.id, msg['clear_list'])                                         
        bot.send_message(message.chat.id, str_customer+list_customer, parse_mode='markdown')


def fields_edit_products_in_admin(bot, prod, chat_id, mess_id=None):
    '''
    Формирование полей и кнопок для товара в админке при редактирование полей.
    '''
    price = '*{}:* {} {}'.format(str(msg['price']), prod.price, prod.currency)
    grand = '*{}:* {} {}'.format(msg['in_stock'], prod.quantity, msg['grand'])
    peace_product = msg['prod_in_desc'] if prod.is_active else msg['prod_from_desc']
    peace_product = '*{}:* {}'.format(msg['peace_product'], peace_product)
    bot.edit_message_caption(
        caption=f'*{prod.title}*\n{price}\n{grand}\n{peace_product}\n\n{prod.description}',
        chat_id=chat_id, 
        message_id=mess_id,
        parse_mode='markdown',
        reply_markup=btn.panel_admin_product(prod.id)
    )


def products_in_admin(message: Message, bot: TeleBot):
    '''
    Список товаров в админке
    '''
    with Session() as session:
        query = session.query(Product).all()
    if not query:
        return bot.send_message(message.chat.id, msg['no_products'])

    for product in query:
        price = '*{}:* {} {}'.format(str(msg['price']), product.price, product.currency)
        grand = '*{}:* {} {}'.format(msg['in_stock'], product.quantity, msg['grand'])
        peace_product = msg['prod_in_desc'] if product.is_active else msg['prod_from_desc']
        peace_product = '*{}:* {}'.format(msg['peace_product'], peace_product)
        bot.send_photo(message.chat.id, 
                    photo=product.photo,
                    caption=f'*{product.title}*\n{price}\n{grand}\n{peace_product}\n\n{product.description}',
                    parse_mode='markdown',
                    reply_markup=btn.panel_admin_product(product.id))


def func_change_count_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Изменение количество товара
    '''
    data: dict = change_count_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    def change_count_product(message: Message):
        if message.text.strip() == 'q' or not message.text.strip().isdigit():
            return 
        with Session() as session:
            session.query(Product).filter_by(id=product_id)\
                                .update({
                                    Product.quantity: int(message.text.strip())
                                })
            prod = session.query(Product).get(product_id)                   
            session.commit()
            fields_edit_products_in_admin(bot, prod, message.chat.id, call.message.message_id)
    
    msg_q = '{}\n\n_{}_'.format(btn.get_text('change_count'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, change_count_product)


def func_change_title_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Изменение заголовка товара
    '''
    data: dict = change_title_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    def change_title_product(message: Message):
        if message.text.strip() == 'q':
            return 
        with Session() as session:
            session.query(Product).filter_by(id=product_id)\
                                .update({
                                    Product.title: message.text
                                })
            prod = session.query(Product).get(product_id)                   
            session.commit()
            fields_edit_products_in_admin(bot, prod, message.chat.id, call.message.message_id)

    msg_q = '{}\n\n_{}_'.format(btn.get_text('change_title_product'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, change_title_product)

def func_change_desc_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Изменение описания товара
    '''
    data: dict = change_desc_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    def change_desc_product(message: Message):
        if message.text.strip() == 'q':
            return 
        with Session() as session:
            session.query(Product).filter_by(id=product_id)\
                                .update({
                                    Product.description: message.text
                                })
            prod = session.query(Product).get(product_id)                   
            session.commit()
            fields_edit_products_in_admin(bot, prod, message.chat.id, call.message.message_id)

    msg_q = '{}\n\n_{}_'.format(btn.get_text('change_desc_product'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, change_desc_product)


def func_change_price_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Изменение цены товара
    '''
    data: dict = change_price_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    def change_price_product(message: Message):
        if message.text.strip() == 'q' or not message.text.strip().isdigit():
            return 
        with Session() as session:
            session.query(Product).filter_by(id=product_id)\
                                .update({
                                    Product.price: int(message.text)
                                })
            prod = session.query(Product).get(product_id)                   
            session.commit()
            fields_edit_products_in_admin(bot, prod, message.chat.id, call.message.message_id)

    msg_q = '{}\n\n_{}_'.format(btn.get_text('change_price_product'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, change_price_product)


def func_remove_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Убрать товар с витрины
    '''
    data: dict = remove_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    with Session() as session:
        session.query(Product).filter_by(id=product_id)\
                            .update({
                                Product.is_active: False
                            })
        prod = session.query(Product).get(product_id)                   
        session.commit()
        price = '*{}:* {} {}'.format(str(msg['price']), prod.price, prod.currency)
        grand = '*{}:* {} {}'.format(msg['in_stock'], prod.quantity, msg['grand'])
        peace_product = msg['prod_in_desc'] if prod.is_active else msg['prod_from_desc']
        peace_product = '*{}:* {}'.format(msg['peace_product'], peace_product)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, 
        message_id=call.message.message_id,reply_markup=None)
        bot.edit_message_caption(
            caption=f'*{prod.title}*\n{price}\n{grand}\n{peace_product}\n\n{prod.description}',
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            parse_mode='markdown',
            reply_markup=btn.panel_admin_product(prod.id)
        )
    bot.send_message(call.message.chat.id, msg['prod_from_desc'], parse_mode='markdown')

def func_add_product_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Добавить товар на витрину
    '''
    data: dict = add_product_admin.parse(callback_data=call.data)
    product_id = data.get('id')
    with Session() as session:
        session.query(Product).filter_by(id=product_id)\
                            .update({
                                Product.is_active: True
                            })
        prod = session.query(Product).get(product_id)                   
        session.commit()
        price = '*{}:* {} {}'.format(str(msg['price']), prod.price, prod.currency)
        grand = '*{}:* {} {}'.format(msg['in_stock'], prod.quantity, msg['grand'])
        peace_product = msg['prod_in_desc'] if prod.is_active else msg['prod_from_desc']
        peace_product = '*{}:* {}'.format(msg['peace_product'], peace_product)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, 
        message_id=call.message.message_id,reply_markup=None)
        bot.edit_message_caption(
            caption=f'*{prod.title}*\n{price}\n{grand}\n{peace_product}\n\n{prod.description}',
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            parse_mode='markdown',
            reply_markup=btn.panel_admin_product(prod.id)
        )
    bot.send_message(call.message.chat.id, msg['prod_in_desc'], parse_mode='markdown')

def create_order_admin(order):
    check_str = ''
    check_str = '*{} №{} от {}*🧾\n\n'.format(msg['check_head'], \
        order.id, order.date.strftime('%d-%m-%Y %H:%M'))
    check_str += '*{}* | *{}* | *{}* | *{}*\n'.format(msg['product'],
                                                msg['price'],
                                                msg['quantity'],
                                                msg['sum'])
    itog = 0                                            
    for product in order.products:
        itog += product.quantity * product.product.price
        check_str += '{}  {} {}  x{}  {} {}\n'.format(product.product.title,
                                            product.product.price,
                                            product.product.currency,
                                            product.quantity,
                                            product.quantity * product.product.price,
                                            product.product.currency)
    check_str += '*{}:* {} {}\n\n'.format(msg['itog'], itog, CURRENCY)

    check_str += '*{}:*\n'.format(msg['customers'])
    check_str += '*{}* | *{}* | *{}* | *{}*\n'\
            .format('ID',msg['last_name'], msg['first_name'],msg['phone_number'])

    check_str += '`{}` {} {} `{}`\n\n'.format(order.customer.user_id,
                                        order.customer.last_name,
                                        order.customer.first_name,
                                        order.customer.phone_number)

    if order.amount == order.payd:
        check_str += '*{}:* {}'.format(msg['status_order'],
                                            msg['order_payd'])  
    else:
        check_str += '*{}:* {} {} / {} {}'.format(msg['status_order'],
                                                order.payd, order.currency,
                                                order.amount, order.currency)
    return check_str

def all_orders_admin(message: Message, bot: TeleBot):
    '''
    Формирование списка заказов и вывод в админке
    '''
    with Session() as session:
        orders = session.query(Order).order_by(Order.date).all()

        for order in orders:
            check_str = create_order_admin(order)
            if order.amount == order.payd:
                bot.send_message(message.chat.id, check_str, parse_mode='markdown')
            else:
                bot.send_message(message.chat.id, check_str, parse_mode='markdown',
                                reply_markup=btn.panel_admin_orders(order.id))


def buy_product(call: types.CallbackQuery, bot: TeleBot):
    '''
    Купить товар
    data: dict = {'@': 'buy_product_id', 'id': '1'}
    '''
    data: dict = buy_product_id.parse(callback_data=call.data)
    product_id = data.get('id')
    func_msg = bot.send_message(call.message.chat.id, msg['request_order'], reply_markup=btn.panel_add_order())

    def func_buy_one_product(message, **kwargs):
        if not message.contact:
            return bot.send_message(message.chat.id, msg['no_order_contact'])
        with Session() as session:
            user = session.query(Customer).filter_by(user_id=message.contact.user_id).first()
            if not user:
                return bot.send_message(message.chat.id, msg['no_search_user'])
            product = session.query(Product).get(kwargs.get('product_id'))
            if not user.phone_number:
                session.query(Customer).filter_by(user_id=message.contact.user_id)\
                                        .update({
                                            Customer.phone_number: message.contact.phone_number
                                        })

            order_user = Order(
                customer = user,
                amount = product.price
            )
            order_user.products.append(
                ProductOrder(
                    order_id = order_user.id,
                    product_id = product.id,
                    currency = product.currency,
                    quantity = 1,
                    amount = product.price
                )
            )
            session.add_all([order_user,])
            session.commit()
            check_str = '*{} №{}* {} 🧾\n\n'.format(msg['check_head'], order_user.id, \
                                                    order_user.date.strftime('%d-%m-%Y %H:%M'))
            check_str += '*{}* | *{}* | *{}* | *{}*\n'.format(msg['product'],
                                                msg['price'],
                                                msg['quantity'],
                                                msg['sum'])
            check_str += '{}  {} {}  x{}  {} {}\n'.format(product.title,
                                            product.price,
                                            product.currency,
                                            1,
                                            product.price,
                                            product.currency)
            check_str += '\n*{}:* {} {}'.format(msg['itog'], product.price, product.currency)

            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, msg['success_contact'])
            bot.send_message(message.chat.id, check_str, parse_mode='markdown')
            callback_notification_admin(bot, order_user.id)
    bot.register_next_step_handler(func_msg, func_buy_one_product, product_id=product_id)


def func_pay_order_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Полностью оплатить заказ
    '''
    data: dict = pay_order_admin.parse(callback_data=call.data)
    order_id = data.get('id')

    def next_pay_order_admin(message: Message, **kwargs):
        old_sum = 0
        if not message.text.strip() == '+':
            return bot.send_message(message.chat.id, msg['no_change_data'])
        
        with Session() as session:
            order = session.query(Order).get(kwargs.get('order_id'))
            old_sum = order.payd
            session.query(Order).filter_by(id=kwargs.get('order_id'))\
                                .update(
                                    {
                                        Order.payd: Order.amount
                                    }
                                )
            session.commit()                    
            check_str = create_order_admin(order)
            bot.edit_message_text(chat_id=message.chat.id, text=check_str, message_id=kwargs.get('msg_id'), parse_mode='markdown')
            back_msg =  '{} {} -> {} {}'.format(old_sum, order.currency, order.payd, order.currency)
            bot.send_message(call.message.chat.id, back_msg, parse_mode='markdown')

    msg_q = '{}\n\n_{}_'.format(btn.get_text('pay_order_admin'), msg['accept_pay'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, next_pay_order_admin, order_id=order_id, msg_id=call.message.message_id)

def func_plus_price_order_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Увеличение суммы 
    '''
    data: dict = plus_price_order_admin.parse(callback_data=call.data)
    order_id = data.get('id')

    def next_plus_price_order_admin(message: Message, **kwargs):
        if message.text.strip() == 'q':
            return bot.send_message(message.chat.id, msg['no_change_data'])
        price = message.text
        if not price.isdigit():
            return bot.send_message(message.chat.id, msg['no_change_data'])
        
        with Session() as session:
            order = session.query(Order).get(kwargs.get('order_id'))
            sum = order.payd + int(price)
            old_sum = order.payd
            back_sum = 0
            markup_btn = None
            if order.amount < sum:
                back_sum = sum - order.amount
                sum = order.amount

            session.query(Order).filter_by(id=kwargs.get('order_id'))\
                                .update(
                                    {
                                        Order.payd: sum
                                    }
                                )
            session.commit()
            if order.amount > order.payd:
                markup_btn = btn.panel_admin_orders(order.id)                    
            check_str = create_order_admin(order)
            bot.edit_message_text(chat_id=message.chat.id, text=check_str, message_id=kwargs.get('msg_id'), 
                                    parse_mode='markdown', reply_markup=markup_btn)
            back_msg =  '{} {} -> {} {}'.format(old_sum, order.currency, sum, order.currency)
            bot.send_message(call.message.chat.id, back_msg, parse_mode='markdown')
            if back_sum:
                back_msg =  '*{}:* {} {}'.format(msg['back_money'], back_sum, order.currency)
                bot.send_message(call.message.chat.id, back_msg, parse_mode='markdown')

    msg_q = '{}\n\n_{}_'.format(btn.get_text('plus_price_order_admin'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, next_plus_price_order_admin, order_id=order_id, msg_id=call.message.message_id)


def func_change_price_order_admin(call: types.CallbackQuery, bot: TeleBot):
    '''
    Изменение суммы оплаты
    '''
    data: dict = change_price_order_admin.parse(callback_data=call.data)
    order_id = data.get('id')

    def next_change_price_order_admin(message: Message, **kwargs):
        markup_btn = None
        old_sum = 0
        if message.text.strip() == 'q':
            return bot.send_message(message.chat.id, msg['no_change_data'])
        price = message.text
        if not price.isdigit():
            return bot.send_message(message.chat.id, msg['no_change_data'])
        
        with Session() as session:
            order = session.query(Order).get(kwargs.get('order_id'))
            old_sum = order.payd
            if order.amount < int(price):
                return bot.send_message(message.chat.id, msg['no_change_data'])
            session.query(Order).filter_by(id=kwargs.get('order_id'))\
                                .update(
                                    {
                                        Order.payd: int(price)
                                    }
                                )
            session.commit()                    
            check_str = create_order_admin(order)
            if order.amount > order.payd:
                markup_btn = btn.panel_admin_orders(order.id)
            bot.edit_message_text(chat_id=message.chat.id, text=check_str, message_id=kwargs.get('msg_id'),
                                 parse_mode='markdown', reply_markup=markup_btn)
            back_msg =  '{} {} -> {} {}'.format(old_sum, order.currency, order.payd, order.currency)
            bot.send_message(call.message.chat.id, back_msg, parse_mode='markdown')                     

    msg_q = '{}\n\n_{}_'.format(btn.get_text('change_price_order_admin'), msg['quit_from_edit'])
    msg_step = bot.send_message(call.message.chat.id, msg_q, parse_mode='markdown')
    bot.register_next_step_handler(msg_step, next_change_price_order_admin, order_id=order_id, msg_id=call.message.message_id)
