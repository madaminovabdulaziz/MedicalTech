from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def order_button(user_id):
    btn = InlineKeyboardMarkup(row_width=2)
    btn.insert(InlineKeyboardButton(text="🗑 Savatni tozalash", callback_data='basket:clear'))
    btn.insert(InlineKeyboardButton(text="🚖 Buyurtma qilish", callback_data=f'basket:submit:{user_id}'))
    return btn