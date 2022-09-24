# filters
from filters import (AdminFilter, ParsePrefix, in_basket_product_id, 
                    buy_product_id, minus_product_id, plus_product_id,
                    delete_product_id, change_count_product_admin,
                    remove_product_admin, add_product_admin, change_desc_product_admin,
                    change_price_product_admin, change_title_product_admin,
                    pay_order_admin, plus_price_order_admin, change_price_order_admin)
from telebot.custom_filters import TextMatchFilter
# handlers
from handlers import (get_me, shop_admin, shop_user,
                    admin_panel, shop_list_product,
                    add_in_basket, buy_product, 
                    list_in_basket, minus_product_in_basket,
                    add_product_in_basket, delete_product_in_basket,
                    add_product_order, send_my_contact,
                    customer_in_admin, products_in_admin,
                    func_add_product_admin, func_remove_product_admin,
                    func_change_count_product_admin, func_change_desc_product_admin,
                    func_change_price_product_admin, func_change_title_product_admin,
                    all_orders_admin, func_pay_order_admin,
                    func_plus_price_order_admin, func_change_price_order_admin,
                    get_image_id)
# config
import config
from buttons import BuildButtons

import flask

from telebot import TeleBot, types
bot = TeleBot(config.TOKEN, num_threads=5)
btn = BuildButtons()


def register_handlers():
    '''
    Функции для администраторов
    '''
    bot.register_message_handler(shop_admin, commands=['start'], pass_bot=True, admin=True)
    bot.register_message_handler(get_image_id, text=[btn.get_text('id_from_photo')], pass_bot=True, admin=True)
    bot.register_message_handler(admin_panel, text=[btn.get_text('admin_panel')], pass_bot=True, admin=True)
    bot.register_message_handler(shop_admin, text=[btn.get_text('back_shop')], pass_bot=True, admin=True)
    bot.register_message_handler(customer_in_admin, text=[btn.get_text('admin_users')], pass_bot=True, admin=True)
    bot.register_message_handler(products_in_admin, text=[btn.get_text('admin_products')], pass_bot=True, admin=True)
    bot.register_message_handler(all_orders_admin, text=[btn.get_text('admin_orders')], pass_bot=True, admin=True)

    # Изменение полей для продуктов
    bot.register_callback_query_handler(func_change_title_product_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=change_title_product_admin.filter())
    bot.register_callback_query_handler(func_change_desc_product_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=change_desc_product_admin.filter())
    bot.register_callback_query_handler(func_change_price_product_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=change_price_product_admin.filter())
    bot.register_callback_query_handler(func_change_count_product_admin, func=None, pass_bot=True,
                                         admin=True, parse_prefix=change_count_product_admin.filter())
    bot.register_callback_query_handler(func_remove_product_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=remove_product_admin.filter())
    bot.register_callback_query_handler(func_add_product_admin, func=None, pass_bot=True,
                                         admin=True, parse_prefix=add_product_admin.filter())
    
    # Изменение полей для заказов
    bot.register_callback_query_handler(func_pay_order_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=pay_order_admin.filter())
    bot.register_callback_query_handler(func_plus_price_order_admin, func=None, pass_bot=True, 
                                        admin=True, parse_prefix=plus_price_order_admin.filter())
    bot.register_callback_query_handler(func_change_price_order_admin, func=None, pass_bot=True,
                                         admin=True, parse_prefix=change_price_order_admin.filter())

    '''
    Функции для пользователей
    '''
    bot.register_message_handler(shop_user, commands=['start'], pass_bot=True, admin=False)

    '''
    Функции для всех
    '''
    bot.register_message_handler(send_my_contact, content_types=['contact'], pass_bot=True)
    bot.register_message_handler(shop_list_product, text=[btn.get_text('products')], pass_bot=True)
    bot.register_message_handler(list_in_basket, text=[btn.get_text('basket')], pass_bot=True)
    bot.register_message_handler(add_product_order, text=[btn.get_text('add_order')], pass_bot=True)
    bot.register_message_handler(get_me, commands=['getme'], pass_bot=True)

    # Действие с товаром из списка товаров
    bot.register_callback_query_handler(add_in_basket, func=None, pass_bot=True, 
                                        parse_prefix=in_basket_product_id.filter())
    bot.register_callback_query_handler(buy_product, func=None, pass_bot=True,
                                         parse_prefix=buy_product_id.filter())

    # Действие с товаром из корзины
    bot.register_callback_query_handler(add_product_in_basket, func=None, pass_bot=True, 
                                        parse_prefix=plus_product_id.filter())
    bot.register_callback_query_handler(minus_product_in_basket, func=None, pass_bot=True, 
                                        parse_prefix=minus_product_id.filter())
    bot.register_callback_query_handler(delete_product_in_basket, func=None, pass_bot=True,
                                        parse_prefix=delete_product_id.filter())

register_handlers()

bot.add_custom_filter(AdminFilter())
bot.add_custom_filter(TextMatchFilter())
bot.add_custom_filter(ParsePrefix())

app = flask.Flask(__name__)
@app.route('/bot', methods=['POST'])
def run_flask():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

def run():
    bot.infinity_polling()

# run()