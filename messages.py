
REQUEST_ORDER = '''
📲 Для завершения оформления заказа отправтье нам свой контакт, чтобы наш специалист связался с вами.
'''
SUCCESS_CONTACT = '''
✅ Ваша заявка была успешно зарегистрированна. Наш специались скоро свяжется с вами.
'''

MESSAGES_RUS = {
    'wellcom': 'Добро пожаловать, %s, в магазин товаров.',
    'first_name': 'Имя',
    'last_name': 'Фамилия',
    'wellcom_admin': 'Добро пожаловать, %s, в панель администраторов.',
    'no_products': 'Товаров нет.',
    'price': 'Цена за 1 штуку',
    'in_stock': 'На складе',
    'grand': 'шт.',
    'add_product': 'Товар добавлен в корзину.',
    'clear_basket': 'Ваша корзина пуста.',
    'sum': 'Сумма',
    'quantity': 'Количество',
    'itog': 'Итого',
    'delete_product': 'Товар удален из корзины.',
    'no_order': 'Невозможно оформить заказ. Ваша корзина пуста.',
    'request_order': REQUEST_ORDER,
    'success_contact': SUCCESS_CONTACT,
    'accept_phone': '✅',
    'no_search_user': 'Мы не смогли найти вас в нашей базе. Попробуйте связаться с тех поддержкой.',
    'no_product_basket': 'Такого товара нет в корзине.',
    'check_head': 'Чек',
    'product': 'Товар',
    'chat': 'Чат',
    'new_order_shop': 'В телеграм-магазине есть новый заказ.',
    'product_check': 'Товарный чек',
    'customers': 'Покупатели',
    'phone_number': 'Номер телефона',
    'clear_list': 'Список пуст.',
    'products': 'Товары',
    'quit_from_edit': 'Отправте "q", чтобы выйти из редактора, не изменяя само поле.',
    'prod_from_desc': 'Товар убран с ветрины.',
    'prod_in_desc': 'Товар выставлен на витрину.',
    'peace_product': 'Расположение товара',
    'no_order_contact': 'Заказ не был сформирован.',
    'status_order':'Статус заказа',
    'accept_pay': 'Отправте "+", чтобы подтвердить свое решение.',
    'no_change_data': 'Данные не были измененны.',
    'order_payd': 'Оплачен✅',
    'back_money': 'Сдача',
    'get_image': 'Загрузите изображение.'
}

class Messages:

    def __init__(self, code='ru'):
        if code == 'ru':
            self.messages = MESSAGES_RUS

    def __getitem__(self, key):
        return self.messages.get(key)