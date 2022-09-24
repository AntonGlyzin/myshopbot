from telebot import types
from filters import (in_basket_product_id, buy_product_id,
                    minus_product_id, plus_product_id, delete_product_id,
                    change_count_product_admin, add_product_admin,
                    remove_product_admin, change_desc_product_admin,
                    change_price_product_admin, change_title_product_admin,
                    pay_order_admin, plus_price_order_admin, change_price_order_admin)

TEXT_BUTTONS_RUS = {
    'admin_panel': '🔑 Админ панель',
    'back_shop': '< Назад в магазин',
    'admin_products': '📦 Товары',
    'admin_users': '👤 Покупатели',
    'admin_orders': '📋 Заказы',
    'id_from_photo': '🖼 ID по фото',
    'products': '🛍 Товары',
    'basket': '🛒 Корзина',
    'in_basket': 'В корзину 🛒',
    'buy': 'Купить 💳',
    'plus': '➕',
    'minus': '➖',
    'delete': '❌',
    'add_order': '🧾 Оформить заказ',
    'request_contact': '📲 Отправить контакт',
    'remove_from_desk': '📥 Убрать',
    'add_in_desk': '📤 На витрину',
    'change_count': '📊 Количество',
    'change_title_product': '📝 Заголовок',
    'change_desc_product': '📝 Описание',
    'change_price_product': '💵 Цена',
    'pay_order_admin': 'Оплатить полностью 💳',
    'plus_price_order_admin': 'Оплатить частью...💵',
    'change_price_order_admin': 'Изменить сумму... '
}

class BuildButtons:

    def __init__(self, code='ru'):
        if code == 'ru':
            self.text_btn = TEXT_BUTTONS_RUS

    def get_text(self, key):
        return self.text_btn.get(key)

    def get_button(self, key):
        return types.KeyboardButton(self.text_btn[key])

    def get_inline_button(self, key, callback_data=None, pay=None):
        return types.InlineKeyboardButton(self.text_btn[key],
                                            callback_data=callback_data)

    def main_menu_user(self):
        markup = types.ReplyKeyboardMarkup(row_width=2, 
                                            resize_keyboard=True)
        return markup.add(
            self.get_button('products'),
            self.get_button('basket')
        ).row(
            self.get_button('add_order'),
        )

    def main_menu_admin(self):
        markup = types.ReplyKeyboardMarkup(row_width=1, 
                                            resize_keyboard=True)
        markup.add(self.get_button('admin_panel'))
        markup.row(
            self.get_button('products'),
            self.get_button('basket')
        ).row(
            self.get_button('add_order'),
        )
        return markup

    def admin_panel(self):
        markup = types.ReplyKeyboardMarkup(row_width=1, 
                                            resize_keyboard=True)
        return markup.row(
            self.get_button('back_shop'),
        ).row(
            self.get_button('admin_products'),
            self.get_button('admin_users'),
        ).row(
            self.get_button('admin_orders'),
            self.get_button('id_from_photo')
        )

    def panel_under_product(self, id_product):
        markup = types.InlineKeyboardMarkup()
        return markup.row(
            self.get_inline_button('buy', buy_product_id.new(id=id_product)),
            self.get_inline_button('in_basket', in_basket_product_id.new(id=id_product))
        )

    def panel_product_basket(self, id_product):
        markup = types.InlineKeyboardMarkup()
        return markup.row(
            self.get_inline_button('plus', plus_product_id.new(id=id_product)),
            self.get_inline_button('minus', minus_product_id.new(id=id_product)),
            self.get_inline_button('delete', delete_product_id.new(id=id_product))
        )

    def panel_add_order(self):
        markup = types.ReplyKeyboardMarkup(row_width=1, 
                                            resize_keyboard=True)
        markup.row(
            self.get_button('back_shop'),
            types.KeyboardButton(self.text_btn['request_contact'], request_contact=True)
        )
        return markup

    def panel_admin_product(self, id_product):
        markup = types.InlineKeyboardMarkup(row_width=2)
        return markup.add(
            self.get_inline_button('change_title_product', change_title_product_admin.new(id=id_product)),
            self.get_inline_button('change_desc_product', change_desc_product_admin.new(id=id_product)),
            self.get_inline_button('change_price_product', change_price_product_admin.new(id=id_product)),
            self.get_inline_button('change_count', change_count_product_admin.new(id=id_product)),
            self.get_inline_button('add_in_desk', add_product_admin.new(id=id_product)),
            self.get_inline_button('remove_from_desk', remove_product_admin.new(id=id_product)),
        )

    def panel_admin_orders(self, id_order):
        markup = types.InlineKeyboardMarkup(row_width=1)
        return markup.add(
            self.get_inline_button('pay_order_admin', pay_order_admin.new(id=id_order)),
            self.get_inline_button('plus_price_order_admin', plus_price_order_admin.new(id=id_order)),
            self.get_inline_button('change_price_order_admin', change_price_order_admin.new(id=id_order)),
        )