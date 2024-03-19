from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart
from utils.db_api.database import Session
from models import Users, Products, Cart, Categories
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from keyboards.default.main_menu import menu_ru
from states.main_states import Main
from keyboards.default.main_menu import basket_and_back
from .messages import product_message


async def create_keyboard(current_value: int, product_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.row(
        
        InlineKeyboardButton(text="➖", callback_data="decrement"),
        InlineKeyboardButton(text=str(current_value), callback_data="zero"),
        InlineKeyboardButton(text="➕", callback_data="increment")
    )
    # Add buttons from 10 to 100 with step 10
    for i in range(0, 101, 10):
        keyboard.insert(InlineKeyboardButton(text=str(i), callback_data=str(i)))
    keyboard.insert(InlineKeyboardButton(text='200', callback_data='200'))

    keyboard.insert(InlineKeyboardButton(text="📥 Добавить в корзину", callback_data=f'add:{product_id}'))

    return keyboard



async def categories_markup():
    db = Session()
    try:
        categories_markup = InlineKeyboardMarkup(row_width=1)
        categories = db.query(Categories).all()
        for category in categories:
            categories_markup.insert(InlineKeyboardButton(text=f'{category.category}', callback_data=f'client:category:{category.id}'))

        return categories_markup

    finally:
        db.close()


async def products_markup_uz(category_id):
    db = Session()
    try:
        products_markup = InlineKeyboardMarkup(row_width=1)
        products = db.query(Products).filter(Products.category_id == category_id).all()
        for product in products:
            products_markup.insert(InlineKeyboardButton(text=f'{product.title}', callback_data=f'client:product:{product.id}'))
        
        products_markup.insert(InlineKeyboardButton(text="📥 Корзина", callback_data=f'client:product:basket'))
        products_markup.insert(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'client:product:back'))

        return products_markup
    finally:
        db.close()




# @dp.message_handler(content_types=types.ContentType.PHOTO, state="*")
# async def getphotoid(message: types.Message):
#     await message.answer(message.photo[-1].file_id)


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    db = Session()
    try:
        # Extract command arguments
        command_args = message.get_args().split('-')
        
        
        if len(command_args) == 2 and command_args[0] == 'product':
            product_id = command_args[1]
            await state.update_data({"pr_id": product_id})
            print(f"Product id from link>>>: {product_id}")
            product = db.query(Products).filter(Products.id == product_id).first()
            keyboard = InlineKeyboardMarkup(row_width=3)

            keyboard.row(
                InlineKeyboardButton(text="➖", callback_data="decrement"),
                InlineKeyboardButton(text="0", callback_data="zero"),
                InlineKeyboardButton(text="➕", callback_data="increment")
            )
          
            for i in range(0, 101, 10):
                keyboard.insert(InlineKeyboardButton(text=str(i), callback_data=str(i)))

            keyboard.insert(InlineKeyboardButton(text='200', callback_data='200'))
            print(f"Product before turning to keyboard >>>: {product_id}")
            keyboard.insert(InlineKeyboardButton(text="📥 Добавить в корзину", callback_data=f'add:{command_args[1]}'))
            await message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=keyboard)
            await state.set_state('get_quantity_start')
            
            
        else:
    
            is_user = db.query(Users).filter(Users.telegram_id == message.from_user.id).first()
            if is_user:
                await message.answer('🏡 Главное меню', reply_markup=menu_ru)
                await Main.main_menu.set()
            else:
                await message.answer('🏡 Главное меню', reply_markup=menu_ru)
                await Main.main_menu.set()
                new_user = Users(
                    full_name=message.from_user.full_name,
                    telegram_id=message.from_user.id, 
                    username=message.from_user.username,
                    role='client',
                    lang='ru'
                )
                db.add(new_user)
                db.commit()

    finally:
        db.close()




@dp.callback_query_handler(state='get_quantity_start')
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    current_value = int(callback_query.message.reply_markup.inline_keyboard[0][1].text)
    if callback_query.data == 'decrement':
        current_value -= 1
    elif callback_query.data == 'increment':
        current_value += 1
    elif callback_query.data == '0':
        current_value = '0'
    
    elif callback_query.data.startswith('add'):
        if current_value != 0:
            info = callback_query.data.rsplit(":")
            pr_id = info[1]
            print(f"Product id from button>>>: {pr_id}")
            try:
                db = Session()
                is_cart_exists = db.query(Cart).filter(Cart.product_id == pr_id, Cart.user_id == callback_query.from_user.id).first()
                if is_cart_exists:
                    updated_cart = db.query(Cart).filter(Cart.product_id == pr_id, Cart.user_id == callback_query.from_user.id).update({
                        Cart.quantity: Cart.quantity + current_value
                    })
                    db.commit()
                else:
                    new_cart = Cart(
                        user_id=callback_query.from_user.id,
                        product_id=pr_id,
                        quantity=current_value
                    )
                    db.add(new_cart)
                    db.commit()
            finally:
                db.close()
            await callback_query.message.delete()
            info = db.query(Products).filter(Products.id == pr_id).first()
            await callback_query.message.answer("✅ Товар добавлен в корзину!", reply_markup=ReplyKeyboardRemove())
            markup = await products_markup_uz(info.category_id)
            category_info = db.query(Categories).filter(Categories.id == info.category_id).first()
            await callback_query.message.answer(f"📦 Товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()
        else:
            await bot.answer_callback_query(callback_query.id, "Сначала введите количество продукта!", show_alert=True)



    else:
        current_value += int(callback_query.data)

    data = await state.get_data()
    product_id = data.get('pr_id')
    markup = await create_keyboard(current_value, product_id)

    

    if callback_query.message.reply_markup != markup:
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=markup)


