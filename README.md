# Простой телеграм-магазин с админ панелью

## Общий функционал

- Команда /getme для вывода ид, чат-ид, имени и фамилии.
- Каждый посетитель может просматривать товары на витрине.
- Товар можно сразу купить, либо сохранить в корзину.
- В корзине предусмотренна возможность прибавлять, убавлять или удалять товар.
- Оформление заказа происходит при отправке контакта.

|Список товаров|Товар в корзине|Оформление заказа|
|-|-|-|
|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot-2.png?alt=media&token=c9a4df62-72e8-4bea-a5f2-6639ffc4b616)|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot.png?alt=media&token=90d00e64-4581-4b45-8cdd-f893a7a9fa62)|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot-5.png?alt=media&token=b7f49120-21e9-4f31-91f4-e2897d6b980c)|

## Функционал в админ панели

- Каждый аттрибут товара возможно отредактировать на свое усмотрение.
- Любой товар можно убрать с витрины, чтобы клиенты его не видели.
- Сами клиенты сохраняются в отдельном спике.
- Когда клиент оплачивает заказ, кнопки для взаимодействия с заказом исчезают.
- Есть возможность получить ID картинки, чтобы сохранить в БД.
- Уведомление админов при успешном оформление заказа клиентом.


|Товары|Клиенты|Заказы|
|-|-|-|
|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot-6.png?alt=media&token=15237157-98e8-471b-af01-6fd42485e309)|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot-8.png?alt=media&token=692fa16c-8aa3-4394-b26d-d19c0960d99e)|![shopbot](https://firebasestorage.googleapis.com/v0/b/antonio-glyzin.appspot.com/o/shopbot%2FScreenshot-7.png?alt=media&token=0600a0fd-3ec3-499d-9759-b5b8d55151f5)|


## Первоначальные настройки

### Настройка БД
```bash
# сформировать схему базы
alembic revision --autogenerate
# миграция схемы
alembic upgrade <Номер>
```

### Настройка файла конфигурации

Файл конфигурации находится в корневой директории и называется `config.py`.

```python config.py

TOKEN = 'Здесь ваш токен'
DB_FILENAME = 'shop.db'
ADMIN = [333333333,] # вместо 333333333 напишите свой ИД, чтобы войти в админку. Чтобы узнать свой ИД, читайте ниже.
CURRENCY = 'руб.' # Валюта по умолчанию, которая будет сохраняться в БД
CALLBACK_CHAT_NOTIFICATION = [333333333,] # вместо 333333333 напишите свой ИД, чтобы получать уведомления от бота о заказах.

```

### Первый запуск

При первом запуске бота необходимо узнать свой ИД, чтобы работать в админке. Для этого есть команда - `/getme`. 

### Запуск бота от админа

После всех манипуляций с настройками следует послать команду  - `/start`. Только тогда можно будет увидеть кнопку перехода в админ панель.
