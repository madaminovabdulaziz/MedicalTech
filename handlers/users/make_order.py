from aiogram import types
from utils.db_api.database import Session
from models import Users, Categories, Products, Cart, Orders, UserLocations
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from keyboards.default.main_menu import menu_ru
from states.main_states import Main
from .products import products_markup_uz, generate_cart_message, create_basket_keyboard
from keyboards.default.main_menu import phone
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time
import random
from keyboards.default.main_menu import location
from sqlalchemy.orm import joinedload
import requests




def get_adress(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    print(response)
    # data = response.json()
    
    # if 'address' in data:
    #     address = data['display_name']
    #     return address
    
    # return None

async def generate_unique_id():
    timestamp = int(time.time())
    random_number = random.randint(0, 999)  
    unique_id = str(timestamp) + str(random_number)
    return unique_id



def admin_confirmation(order_num, user_id):
    btn = InlineKeyboardMarkup(row_width=2)
    btn.insert(InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f'zakaz:confirm:{order_num}:{user_id}'))
    btn.insert(InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f'zakaz:cancel:{order_num}'))
    return btn


async def get_orders_for_user(admin_id, user_id, or_num):
    session = Session()
    user = session.query(Users).filter(Users.telegram_id == user_id).first()
    result = session.query(UserLocations).filter(UserLocations.user_id == user_id).first()
    adress = result.adress
    user_orders = session.query(Orders).filter(Orders.order_number == or_num, Orders.status == "Pending").all()
    total_sum = 0
    numeration = 1
    message = f"<b>🔥 Yangi buyurtma!</b>\n\n🧾 Buyurtma raqami: #{or_num}\n\n👨‍💻 Buyurtmachi: {user.full_name}\n☎️ Telefon raqami: {user.phone}\n\n"
    message += f"\n📍 Manzil: {adress}\n\n"
    for user_order in user_orders:

        product = user_order.product
        title = product.title
        price = int(product.price)
        quantity = user_order.quantity_ordered

        product_total = quantity * price
        total_sum += product_total

        product_total = "{:,}".format(product_total)
        message += f"{numeration}) {title} x <b>{quantity}</b>-dona = {product_total} so'm\n"
        numeration += 1


    total_sum = "{:,}".format(total_sum)
    message += f"\n\n<b>💵 Umumiy:</b> {total_sum} so'm"
        
    session.close()
    await bot.send_message(chat_id=admin_id, text=message, reply_markup=admin_confirmation(or_num, user_id))

@dp.callback_query_handler(text_contains='basket', state=Main.main_menu)
async def proceedBB(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    way = data[1]
    try:
        info = await state.get_data()
        category_id = info.get('category_id')
        db = Session()
        if way == "back":
            await call.message.delete()
            markup = await products_markup_uz(category_id)
            category_info = db.query(Categories).filter(Categories.id == category_id).first()
            await call.message.answer(f"📦 товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()

        elif way == "clear":
            await call.message.delete()
            db.query(Cart).filter(Cart.user_id == call.from_user.id).delete()
            db.commit()
            markup = await products_markup_uz(category_id)
            category_info = db.query(Categories).filter(Categories.id == category_id).first()
            await call.message.answer(f"📦 товары категории <b>{category_info.category}:</b>", reply_markup=markup)
            await Main.main_menu.set()

        elif way == "delete":
            product_id = data[2]
            db.query(Cart).filter(Cart.product_id == product_id).delete()
            db.commit()
            basket_message = await generate_cart_message(call.from_user.id)
            keyboard = await create_basket_keyboard(call.from_user.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=basket_message, reply_markup=keyboard)
            await Main.main_menu.set()


        elif way == "submit":
            is_registered = db.query(Users).filter(Users.telegram_id == call.from_user.id).first()
            phone = is_registered.phone
            if not phone:
                await call.message.answer('Введите Ваше имя: ', reply_markup=ReplyKeyboardRemove())
                await state.set_state('get_client_name')
            else:
                products_in_cart = db.query(Cart).filter(Cart.user_id == call.from_user.id).all()
                total_sum = 0 
                or_num = await generate_unique_id()
                for product in products_in_cart:
                    mahsulot = product.product
                    product_id = product.product_id
                    quantity = product.quantity
                    product_price = mahsulot.price


                    product_total = quantity * product_price
                    total_sum += product_total


                    new_order = Orders(
                        order_number=or_num,
                        user_id=call.from_user.id,
                        product_id=product_id,
                        quantity_ordered=quantity,
                        total_price=product_total,
                        order_date=datetime.now(),  
                        status="Pending"  
                    )
                    db.add(new_order)

                    db.query(Cart).filter(Cart.user_id == call.from_user.id).delete()
                db.commit()

                await call.message.answer("Ваш заказ принят, администраторы свяжутся с вами в ближайшее время!")
                await call.message.answer('🏡 Главное меню', reply_markup=menu_ru)
                await Main.main_menu.set()
                admins = ['5069131343', '1179337461']
                for i in admins:
                    await get_orders_for_user(i, call.from_user.id, or_num)




    finally:
        db.close()



@dp.message_handler(state='get_client_name')
async def getClinetName(message: types.Message, state: FSMContext):
    name =  message.text
    if name.isdigit():
        await message.answer("Введите свое имя в правильном формате!")
        return
    else:
        await state.update_data({"client_name": name})
        await message.answer("Укажите место доставки", reply_markup=location)
        await state.set_state('get_location')
        


@dp.message_handler(content_types=types.ContentType.LOCATION, state="get_location")
async def getLocationUser(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    adress = get_adress(latitude, longitude)
    db = Session()
    new_loc = UserLocations(
        user_id=message.from_user.id,
        latitude=latitude,
        longitude=longitude,
        adress=adress

    )
    db.add(new_loc)
    db.commit()
    db.close()
    await message.answer("Отправьте или введите ваш номер телефона в формате: +998 ** *** ** ** ", reply_markup=phone)
    await state.set_state('get_client_phone')


@dp.message_handler(content_types=types.ContentType.CONTACT, state='get_client_phone')
async def getContact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    contact = message.contact['phone_number']
    name = data.get('client_name')
    try:
        db = Session()

        user = db.query(Users).filter(Users.telegram_id == message.from_user.id).update({
            Users.full_name: name,
            Users.phone: contact
        })
        db.commit()

        products_in_cart = db.query(Cart).filter(Cart.user_id == message.from_user.id).all()
        total_sum = 0  
        or_num = await generate_unique_id()
        for product in products_in_cart:
            mahsulot = product.product
            product_id = product.product_id
            quantity = product.quantity
            product_price = mahsulot.price


            product_total = quantity * product_price
            total_sum += product_total

                
            new_order = Orders(
                order_number=or_num,
                user_id=message.from_user.id,
                product_id=product_id,
                quantity_ordered=quantity,
                total_price=product_total,
                order_date=datetime.now(), 
                status="Pending"  
            )
            db.add(new_order)

            db.query(Cart).filter(Cart.user_id == message.from_user.id).delete()
        db.commit()

        await message.answer("Ваш заказ принят, администраторы свяжутся с вами в ближайшее время!")
        await message.answer('🏡 Главное меню', reply_markup=menu_ru)
        await Main.main_menu.set()
        admins = ['5069131343', '1179337461']
        for i in admins:
            await get_orders_for_user(i, message.from_user.id, or_num)

    finally:
        db.close()



@dp.message_handler(state='get_client_phone')
async def getContact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    contact = message.text
    name = data.get('client_name')
    try:
        if contact.isdigit():
            if len(contact) == 9:
                db = Session()

                user = db.query(Users).filter(Users.telegram_id == message.from_user.id).update({
                    Users.full_name: name,
                    Users.phone: contact
                })
                db.commit()

                products_in_cart = db.query(Cart).filter(Cart.user_id == message.from_user.id).all()
                total_sum = 0  
                or_num = await generate_unique_id()
                for product in products_in_cart:
                    mahsulot = product.product
                    product_id = product.product_id
                    quantity = product.quantity
                    product_price = mahsulot.price


                    product_total = quantity * product_price
                    total_sum += product_total

                        
                    new_order = Orders(
                        order_number=or_num,
                        user_id=message.from_user.id,
                        product_id=product_id,
                        quantity_ordered=quantity,
                        total_price=product_total,
                        order_date=datetime.now(), 
                        status="Pending"  
                    )
                    db.add(new_order)

                    db.query(Cart).filter(Cart.user_id == message.from_user.id).delete()
                db.commit()

                await message.answer("Ваш заказ принят, администраторы свяжутся с вами в ближайшее время")
                await message.answer('🏡 Главное меню', reply_markup=menu_ru)
                await Main.main_menu.set()
                admins = ['5069131343', '1179337461']
                for i in admins:
                    await get_orders_for_user(i, message.from_user.id, or_num)
                
            else:
                await message.answer("Пожалуйста, введите в правильном формате!")
                return
        else:
            await message.answer("Пожалуйста, введите в правильном формате!")
            return

    finally:
        db.close()


                    

admins = ['5069131343', '1179337461']

@dp.callback_query_handler(text_contains='zakaz', chat_id=admins, state="*")
async def stepswithZakaz(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    order_num = data[2]
    if data[1] == "confirm":
        db = Session()
        db.query(Orders).filter(Orders.order_number == order_num).update({
            Orders.status:"qabul"
        })
        db.commit()

        user_id = data[3]
        loc = db.query(UserLocations).filter(UserLocations.user_id == user_id).first()
        latitude = loc.latitude
        longitude = loc.longitude
        


        db.close()
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        await call.message.reply("Muvaffaqiyatli tasdiqlandi!")
        await call.message.reply_location(latitude, longitude)

                    
