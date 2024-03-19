from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



menu_ru = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔧 Продукты")
        ],
        [
            KeyboardButton(text='🛒 Корзина')
        ],
        [
            KeyboardButton(text='📝 Связаться с нами'),
            KeyboardButton(text='📦 Мои заказы')
        ],
        [
            KeyboardButton(text='🏬 О нас')
        ]
    ],
    resize_keyboard=True, one_time_keyboard=True
)


basket_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛒 Корзина")
        ],
        [
            KeyboardButton(text='⬅️ Назад')
        ]
    ],
    resize_keyboard=True, one_time_keyboard=True
)


phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Мой номер", request_contact=True)
        ]
    ],
    resize_keyboard=True, one_time_keyboard=True
)


location = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📍 Отправить местоположение", request_location=True)
        ]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

