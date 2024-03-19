from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def languages_btn():
    btn = InlineKeyboardMarkup(row_width=1)
    btn.insert(InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data='til:uz'))
    btn.insert(InlineKeyboardButton(text="🇷🇺 Русский", callback_data='til:ru'))
    return btn