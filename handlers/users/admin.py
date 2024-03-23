from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from utils.db_api.database import Session
from models import Orders, Categories, Products, Users
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from keyboards.default.main_menu import menu_ru
from states.main_states import Main
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .messages import product_message
import pandas as pd
from sqlalchemy.orm import joinedload
from datetime import datetime
from io import BytesIO
import pandas as pd
from openpyxl import load_workbook
from sqlalchemy.orm import joinedload
from datetime import datetime
import os

def admins_btn():
    btn = InlineKeyboardMarkup(row_width=1)
    btn.insert(InlineKeyboardButton(text="Mahsulotlar", callback_data='admin:products'))
    btn.insert(InlineKeyboardButton(text="Bazani ko'rish", callback_data='admin:xlsx'))
    
    return btn



def is_sterille():
    btn = InlineKeyboardMarkup(row_width=2)
    btn.insert(InlineKeyboardButton(text="Steril", callback_data='status:steril'))
    btn.insert(InlineKeyboardButton(text="Nosteril", callback_data='status:nosteril'))
    return btn



def condirmation():
    btn = InlineKeyboardMarkup(row_width=2)
    btn.insert(InlineKeyboardButton(text="✅ Tasdiqlash", callback_data='product:confirm'))
    btn.insert(InlineKeyboardButton(text="❌ Bekor qilish", callback_data='product:cancel'))
    return btn


def changelog(category_id, product_id):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.insert(InlineKeyboardButton(text="🔗 Mahsulot uchun link", callback_data=f'change:link:{product_id}'))
    btn.insert(InlineKeyboardButton(text="🔄 Nomini o'zgartirish", callback_data='change:title'))
    btn.insert(InlineKeyboardButton(text="🔄 Narxini o'zgartirish", callback_data='change:price'))
    btn.insert(InlineKeyboardButton(text="🔄 Qo'shimcha ma'lumotni o'zgartirish", callback_data='change:desc'))
    btn.insert(InlineKeyboardButton(text="🔄 Rasmni o'zgartirish", callback_data='change:photo'))
    btn.insert(InlineKeyboardButton(text="⬅️ Ortga", callback_data=f'change:back:{category_id}'))
    btn.insert(InlineKeyboardButton(text="❌ O'chirish", callback_data=f'change:delete:{product_id}'))
   
    return btn


async def categories_markup():
    db = Session()
    try:
        categories_markup = InlineKeyboardMarkup(row_width=1)
        categories = db.query(Categories).all()
        for category in categories:
            categories_markup.insert(InlineKeyboardButton(text=f'{category.category}', callback_data=f'category:{category.id}'))

        categories_markup.insert(InlineKeyboardButton(text='➕ Kategoriya qoshish', callback_data='category:add'))
        categories_markup.insert(InlineKeyboardButton(text='⬅️ Ortga', callback_data=f'category:back'))

        return categories_markup

    finally:
        db.close()


async def products_markup_hey(category_id):
    db = Session()
    try:
        products_markup = InlineKeyboardMarkup(row_width=1)
        products = db.query(Products).filter(Products.category_id == category_id).all()
        for product in products:
            products_markup.insert(InlineKeyboardButton(text=f'{product.title}', callback_data=f'product:{product.id}'))

        products_markup.insert(InlineKeyboardButton(text='➕ Mahsulot qoshish', callback_data=f'product:add'))
        products_markup.insert(InlineKeyboardButton(text="❌ Katigoriyani o'chirish", callback_data=f'product:category:{category_id}'))
        products_markup.insert(InlineKeyboardButton(text='⬅️ Ortga', callback_data=f'product:back'))

        return products_markup
    finally:
        db.close()


admins = ['5069131343', '1179337461', '1002440668']
@dp.message_handler(commands='admin', chat_id=admins, state="*")
async def showPanel(message: types.Message, state: FSMContext):
    await message.answer('Admin panelga xush kelibsiz!', reply_markup=admins_btn())
    await state.set_state('get_admin_option')



@dp.callback_query_handler(text_contains='admin', state='get_admin_option')
async def next_step_1(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")    
    if data[1] == 'products':
        markup = await categories_markup()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Kategoriyani tanlang:", reply_markup=markup)
        await state.set_state('get_categories')
    elif data[1] == "xlsx":
        data = list()
        db = Session()
        orders = db.query(Orders).options(joinedload(Orders.user), joinedload(Orders.product)).all()
        for order in orders:
            order_data = (
                order.id,
                order.user.full_name,
                order.user.phone,
                order.product.title,
                order.quantity_ordered,
                order.total_price,
                order.order_date,
                order.status
            )
            data.append(order_data)

        columns = ['Buyurtma ID', 'Klient', 'Telefon raqami', 'Mahsulot', 'Soni', 'Umumiy narxi', 'Buyurtma sanasi', 'Status']
        df = pd.DataFrame(data, columns=columns)

        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime("%d.%m.%Y")
        excel_file_path = f"files/{formatted_date}.xlsx"

        # Write DataFrame to Excel file
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']  # Change 'Sheet1' to your sheet name if different
            
            # Adjust column widths
            for idx, col in enumerate(df):
                max_length = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[worksheet.cell(row=1, column=idx+1).column_letter].width = max_length

        # Send the Excel file
        with open(excel_file_path, 'rb') as file:
            await bot.send_document(call.from_user.id, file)

        db.close()
        os.remove(excel_file_path)
        

        # data = list()
        # db = Session()
        # orders = db.query(Orders).options(joinedload(Orders.user), joinedload(Orders.product)).all()
        # for order in orders:
        #     order_data = (
        #         order.id,
        #         order.user.full_name,
        #         order.user.phone,
        #         order.product.title,
        #         order.quantity_ordered,
        #         order.total_price,
        #         order.order_date,
        #         order.status
        #     )
        #     data.append(order_data)

        
        # columns = ['Buyurtma ID', 'Klient', 'Telefon raqami','Mahsulot', 'Soni', 'Umumiy narxi', 'Buyurtma sanasi', 'Status']
        # df = pd.DataFrame(data, columns=columns)
        # current_datetime = datetime.now()

        # formatted_date = current_datetime.strftime("%d.%m.%Y")

        # df.to_excel(f"files/{formatted_date}.xlsx", index=False)
        # with open(f"files/{formatted_date}.xlsx", 'rb') as file:
        #     await bot.send_document('1179337461', file)

                
        # db.close()








@dp.callback_query_handler(text_contains='admin', state='get_admin_option')
async def next_step_1(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = call.data.rsplit(":")    
    if data[1] == 'products':
        markup = await categories_markup()
        await call.message.answer("Kategoriyani tanlang:", reply_markup=markup)
        await state.set_state('get_categories')



@dp.callback_query_handler(text_contains='category', state="get_categories")
async def get_category(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    db = Session()
    try:
        if data[1] == "add":
            await call.message.delete()
            await call.message.answer("Kategoriya nomini kiriting: ")
            await state.set_state('get_category_name')
        elif data[1] == "back":
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Admin panelga xush kelibsiz!', reply_markup=admins_btn())
            await state.set_state('get_admin_option')
            
        else:
            category_id = data[1]
            await state.update_data({'category_id':category_id})
            category = db.query(Categories).filter(Categories.id == category_id).first()
            products_markup = await products_markup_hey(category_id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{category.category} - kategoriyasidagi mahsulotlar:', reply_markup=products_markup)
            await state.set_state('get_product')


    finally:
        db.close()



@dp.callback_query_handler(text_contains='product', state='get_product')
async def getProduct(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(':')
    db = Session()
    try:
        if data[1] == "add":
            await call.message.answer('Mahsulot nomini kiriting: ', reply_markup=ReplyKeyboardRemove())
            await state.set_state('get_product_title')

        elif data[1] == "back":
            markup = await categories_markup()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Kategoriyani tanlang', reply_markup=markup)
            await state.set_state('get_categories')
        elif data[1] == "category":
            db.query(Categories).filter(Categories.id == data[2]).delete()
            db.commit()
            await call.message.answer("Kategoriya o'chirildi!")
            markup = await categories_markup()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Kategoriyani tanlang', reply_markup=markup)
            await state.set_state('get_categories')

        
        else:
            await call.message.delete()
            product_id = data[1]
            product = db.query(Products).filter(Products.id == product_id).first()
            await call.message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=changelog(product.category_id, product_id))
            await state.set_state('get_changes')

    except:
        db.close()


@dp.callback_query_handler(text_contains='change',state='get_changes')
async def proceedChanges(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(':')
    if data[1] == "back":
        try:
            await call.message.delete()
            db = Session()
            products = await products_markup_hey(data[2])
            await call.message.answer("Mahsulotni tanlang:", reply_markup=products)
            await state.set_state('get_product')
        finally:
            db.close()

    elif data[1] == "link":
        product_id = data[2]
        link = f"https://t.me/techmedicalbot?start=product-{product_id}"
        await call.message.answer(f"Mahsulot uchun link:\n\n\n{link}")

    
    elif data[1] == "delete":
        try:
            print(data[2])
            db = Session()
            await call.message.delete()
            db.query(Products).filter(Products.id == data[2]).delete()
            db.commit()
            markup = await categories_markup()
            await call.message.answer("✅ O'chirildi!", reply_markup=markup)
            await state.set_state('get_categories')


        finally:
            db.close()

    elif data[1] == 'title':
        await state.update_data({"product_num": data[2]})
        await call.message.answer('Mahsulot nomini kiriting: ')
        await state.set_state('change_title')
    
    elif data[1] == 'price':
        await state.update_data({"product_num": data[2]})
        await call.message.answer('Mahsulot narxini kiriting: ')
        await state.set_state('change_price')

    elif data[1] == 'desc':
        await state.update_data({"product_num": data[2]})
        await call.message.answer("Qo'shimcha ma'lumot kiriting: ")
        await state.set_state('change_desc')

    elif data[1] == 'photo':
        await state.update_data({"product_num": data[2]})
        await call.message.answer("Rasm yuboring: ")
        await state.set_state('change_photo')




@dp.message_handler(state='change_title')
async def ChangeProductTitle(message: types.Message, state: FSMContext):
    new_title = message.text
    data = await state.get_data()
    pr_id = data.get('product_num')
    db = Session()
    db.query(Products).filter(Products.id == pr_id).update({
        Products.title: new_title
    })

    db.commit()
   

    await message.answer("Muvaffaqiyatli o'zgardi!")
    product = db.query(Products).filter(Products.id == pr_id).first()
    await message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=changelog(product.category_id, pr_id))
    await state.set_state('get_changes')
    db.close()



@dp.message_handler(state='change_price')
async def ChangeProductPrice(message: types.Message, state: FSMContext):
    new_price = message.text
    data = await state.get_data()
    pr_id = data.get('product_num')
    db = Session()
    if new_price.isdigit():
        db.query(Products).filter(Products.id == pr_id).update({
        Products.price: new_price
        })
        db.commit()
        

        await message.answer("Muvaffaqiyatli o'zgardi!")
        product = db.query(Products).filter(Products.id == pr_id).first()
        await message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=changelog(product.category_id, pr_id))
        await state.set_state('get_changes')     
        db.close()
    else:
        await message.answer('Iltimos, narxni faqat son tarzda kiriting!')
        return
    



@dp.message_handler(state='change_desc')
async def ChangeProductDesc(message: types.Message, state: FSMContext):
    new_desc = message.text
    data = await state.get_data()
    pr_id = data.get('product_num')
    db = Session()
    db.query(Products).filter(Products.id == pr_id).update({
        Products.description: new_desc
    })

    db.commit()
    

    await message.answer("Muvaffaqiyatli o'zgardi!")
    product = db.query(Products).filter(Products.id == pr_id).first()
    await message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=changelog(product.category_id, pr_id))
    await state.set_state('get_changes')
    db.close()



@dp.message_handler(content_types=types.ContentType.PHOTO, state='change_photo')
async def ChangeProductPhoto(message: types.Message, state: FSMContext):
    photoss = message.photo[-1].file_id
    print(photoss)
    data = await state.get_data()
    pr_id = data.get('product_num')
    print(pr_id)
    db = Session()
    # print(pr_id)
    if db.query(Products).filter(Products.id == pr_id).first():
        db.query(Products).filter(Products.id == pr_id).update({
            Products.photo_id: photoss
        })

        db.commit()
        print("RASM COMMIT")
        

        await message.answer("Muvaffaqiyatli o'zgardi!")
        product = db.query(Products).filter(Products.id == pr_id).first()
        await message.answer_photo(photo=product.photo_id, caption=product_message(product.title, product.price, product.sterile_status, product.description), reply_markup=changelog(product.category_id, pr_id))
        await state.set_state('get_changes')
        db.close()




@dp.message_handler(state="get_category_name")
async def saveCategory(message: types.Message, state: FSMContext):
    db = Session()
    try:
        category_title = message.text
        new_category = Categories(
            category=category_title
        )
        db.add(new_category)
        db.commit()
       
        categories_markup = InlineKeyboardMarkup(row_width=1)
        categories = db.query(Categories).all()
        for category in categories:
            categories_markup.insert(InlineKeyboardButton(text=f'{category.category}', callback_data=f'category:{category.id}'))

        categories_markup.insert(InlineKeyboardButton(text='➕ Kategoriya qoshish', callback_data=f'category:add'))
        await message.answer("Kategoriya qo'shildi!", reply_markup=categories_markup)
        #await message.answer("Kategoriyani tanlang:", reply_markup=categories_markup)
        await state.set_state('get_categories')
    finally:
        db.close()


@dp.message_handler(state='get_product_title')
async def getProductName(message: types.Message, state: FSMContext):
    title = message.text

    await state.update_data({'title': title})
    await message.answer('Mahsulot narxini kiriting: ')
    await state.set_state('get_product_price')

@dp.message_handler(state='get_product_price')
async def getProductPrice(message: types.Message, state: FSMContext):
    price = message.text
    if price.isdigit():
        await state.update_data({'price': price})
        await message.answer('Sterillik statusini tanlang', reply_markup=is_sterille())
        await state.set_state('get_sterille_status')

    else:
        await message.answer('Iltimos, narxni faqat son tarzda kiriting!')
        return


@dp.callback_query_handler(text_contains='status', state='get_sterille_status')
async def getSterilleStatus(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    await state.update_data({'is_sterile': data[1]})
    await call.message.answer("Qo'shimcha ma'lumot kiriting: ")
    await state.set_state('get_description')


@dp.message_handler(state='get_description')
async def getDescription(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data({'description': description})
    await message.answer("Mahsulot rasmini kiriting")
    await state.set_state('get_product_photo')  


@dp.message_handler(content_types=types.ContentType.PHOTO, state='get_product_photo')
async def getPhoto(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data({"photo": photo})

    data = await state.get_data()
    title = data.get('title')
    price = data.get('price')
    is_sterile = data.get('is_sterile')
    description = data.get('description')


    await message.answer_photo(photo=photo, caption=product_message(title, price, is_sterile, description), reply_markup=condirmation())
    await state.set_state('wait_for_confirm')


@dp.callback_query_handler(text_contains='product', state='wait_for_confirm')
async def getForConfirmation(call: CallbackQuery, state: FSMContext):
    info = call.data.rsplit(':')
    db = Session()
    try:
        if info[1] == "confirm":
            data = await state.get_data()

            category_id = data.get('category_id')
            title = data.get('title')
            price = data.get('price')
            is_sterile = data.get('is_sterile')
            description = data.get('description')
            photo = data.get('photo')

            new_Product = Products(
                title=title,
                category_id=category_id,
                price=price,
                sterile_status=is_sterile,
                description=description,
                photo_id=photo
            )

            db.add(new_Product)
            db.commit()

            await call.message.answer("✅ Mahsulot qo'shildi!")
            markup = await categories_markup()
            await call.message.answer("Kategoriyani tanlang:", reply_markup=markup)
            await state.set_state('get_categories')
    finally:

        db.close()



@dp.message_handler(commands=['buy'], state="*")
async def buy(message: types.Message):
    # Create an invoice
    invoice = types.LabeledPrice(label='Product', amount=1000)  # Amount is in smallest currency unit (e.g., cents)
    await bot.send_invoice(message.chat.id, title='Product', description='Description of the product', payload='payload', provider_token='your_provider_token', start_parameter='start_parameter', currency='USD', prices=[invoice])

@dp.message_handler(content_types=['successful_payment'])
async def successful_payment(message: types.Message):
    # Handle successful payment
    await message.answer('Thank you for your payment!')
