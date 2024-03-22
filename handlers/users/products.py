from aiogram import types
from utils.db_api.database import Session
from models import Users, Categories, Products, Cart
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from states.main_states import Main
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .messages import product_message
from keyboards.default.main_menu import basket_and_back


async def create_basket_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(InlineKeyboardButton(text='⬅️ Назад', callback_data='basket:back'))
    keyboard.insert(InlineKeyboardButton(text='🗑 Очистить корзину', callback_data='basket:clear'))
    keyboard.insert(InlineKeyboardButton(text='🚖 Оформить', callback_data=f'basket:submit'))
        

    try:
        session = Session()
        user = session.query(Users).filter(Users.telegram_id == user_id).first()
        user_cart = user.cart
        if user_cart:
            for product in user_cart:
                product = product.product 
                product_name = product.title

                keyboard.add(InlineKeyboardButton(text=f"❌ {product_name}", callback_data=f"basket:delete:{product.id}"))

            
            return keyboard



    finally:
        session.close()



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




async def generate_cart_message(telegram_id):
    try:
        session = Session()
        user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
        if user:
            
            user_cart = user.cart
           
            if user_cart:
                message = "<b>📥 Ваша корзина:</b>\n\n"

                total_sum = 0  

                for cart_item in user_cart:
                    product = cart_item.product 
                    product_name = product.title
                    quantity = cart_item.quantity
                    product_price = int(product.price)


                    product_total = quantity * product_price
                    total_sum += product_total
                    product_total = '{:,}'.format(product_total)

                    message += f"{product_name} ✖️ {quantity} = {product_total}\n\n"


                total_sum = '{:,}'.format(total_sum)
                message += f"\n\n<b>Общий:</b> {total_sum}-сум\n\n"
                message += f"🚖 Бесплатная доставка по городу Ташкент!"
            else:
                return 'Ваша корзина пуста!'

        else:
            pass

    finally:
        session.close()

    return message



products_buttons = ['🔧 Продукты']
category_image = 'AgACAgIAAxkBAAMaZfngu0OnF1sowu33GnHSW7OaQV8AAlPWMRt-JNFLhRrDDO4Z-m4BAAMCAAN4AAM0BA'

@dp.message_handler(text=products_buttons, state=Main.main_menu)
async def showCategoriesUser(message: types.Message, state: FSMContext):

    markup = await categories_markup()
    await message.answer_photo(photo=category_image, caption='<b>🗂️ Выберите категорию:</b>', reply_markup=markup)
    await Main.main_menu.set()




@dp.callback_query_handler(text_contains='client', state=Main.main_menu)
async def showProducts(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    try:
        db = Session()
        user = db.query(Users).filter(Users.telegram_id == call.from_user.id).first()
        if data[1] == "category":
            category_id = data[2]
            await state.update_data({"category_id": category_id})
            await call.message.delete()
            category_info = db.query(Categories).filter(Categories.id == category_id).first()
            markup = await products_markup_uz(category_id)
            await call.message.answer(f"📦 товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()

        elif data[1] == "product":
            product_id = data[2]
            await state.update_data({'product_id_basket':product_id})
            if product_id == "back":
                await call.message.delete()
                markup = await categories_markup()
                await call.message.answer_photo(photo=category_image, caption='<b>🗂️ Выберите категорию:</b>', reply_markup=markup)
                await Main.main_menu.set()
            elif product_id == "basket":

                cart_msg = await generate_cart_message(call.from_user.id)
                if cart_msg:
                    await call.message.delete()
                    keyboard_buttons = await create_basket_keyboard(call.from_user.id)
                    await call.message.answer(cart_msg, reply_markup=keyboard_buttons)
                    await Main.main_menu.set()
                else:
                    await call.message.answer("Ваша корзина пуста!")
            else:
                await call.message.delete()
                product = db.query(Products).filter(Products.id == product_id).first()
                keyboard = InlineKeyboardMarkup(row_width=3)

                keyboard.row(
                    InlineKeyboardButton(text="➖", callback_data="decrement"),
                    InlineKeyboardButton(text="0", callback_data="zero"),
                    InlineKeyboardButton(text="➕", callback_data="increment")
                )
                # Add buttons from 10 to 100 with tep 10
                for i in range(0, 101, 10):
                    keyboard.insert(InlineKeyboardButton(text=str(i), callback_data=str(i)))

                keyboard.insert(InlineKeyboardButton(text='200', callback_data='200'))
                keyboard.insert(InlineKeyboardButton(text="📥 Добавить в корзину", callback_data=f'add:{product_id}'))
                a = await call.message.answer("Выберите одно из следующих: ", reply_markup=basket_and_back)
                await call.message.answer_photo(photo=product.photo_id,caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=keyboard)
                await state.set_state('get_quantity')
                



    finally:
        db.close()



basket_btns = ['🛒 Корзина', '⬅️ Назад']
@dp.message_handler(text=basket_btns, state='get_quantity')
async def proceedbasketbtn(message: types.Message, state: FSMContext):
    if message.text == basket_btns[0]:
        cart_msg = await generate_cart_message(message.from_user.id)
        if cart_msg:
            keyboard_order = await create_basket_keyboard(message.from_user.id)
            await message.answer(cart_msg, reply_markup=keyboard_order)
            await Main.main_menu.set()
        else:
            await message.answer("Ваша корзина пуста!")

    elif message.text == basket_btns[1]:
        try:
            
            db = Session()
            info = await state.get_data()
            category_id = info.get('category_id')

            markup = await products_markup_uz(category_id)
            category_info = db.query(Categories).filter(Categories.id == category_id).first()
            await message.answer(f"📦 товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()
        finally:
            db.close()



@dp.callback_query_handler(state='get_quantity')
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
            info = await state.get_data()
            category_id = info.get('category_id')
            await callback_query.message.answer("✅Товар добавлен в корзину!", reply_markup=ReplyKeyboardRemove())
            markup = await products_markup_uz(category_id)
            category_info = db.query(Categories).filter(Categories.id == category_id).first()
            await callback_query.message.answer(f"📦 товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()
        else:
            await bot.answer_callback_query(callback_query.id, "Сначала введите количество продукта!", show_alert=True)



    else:
        current_value += int(callback_query.data)

    data = await state.get_data()
    product_id = data.get('product_id_basket')
    markup = await create_keyboard(current_value, product_id)

    

    if callback_query.message.reply_markup != markup:
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=markup)
