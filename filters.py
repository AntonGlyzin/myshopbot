from telebot.custom_filters import SimpleCustomFilter
from telebot import types, AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from config import ADMIN


class AdminFilter(SimpleCustomFilter):
    key = 'admin'
    def check(self, message):
        return int(message.from_user.id) in ADMIN


in_basket_product_id = CallbackData("id", prefix="in_basket_product_id")
buy_product_id = CallbackData("id", prefix="buy_product_id")
plus_product_id = CallbackData("id", prefix="plus_product_id")
minus_product_id = CallbackData("id", prefix="minus_product_id")
delete_product_id = CallbackData("id", prefix="delete_product_id")

add_product_admin = CallbackData("id", prefix="add_product_admin")
remove_product_admin = CallbackData("id", prefix="remove_product_admin")
change_count_product_admin = CallbackData("id", prefix="change_count_product_admin")
change_title_product_admin = CallbackData("id", prefix="change_title_product_admin")
change_desc_product_admin = CallbackData("id", prefix="change_desc_product_admin")
change_price_product_admin = CallbackData("id", prefix="change_price_product_admin")

change_price_order_admin = CallbackData("id", prefix="change_price_order_admin")
plus_price_order_admin = CallbackData("id", prefix="plus_price_order_admin")
pay_order_admin = CallbackData("id", prefix="pay_order_admin")
class ParsePrefix(AdvancedCustomFilter):
    key = 'parse_prefix'
    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
