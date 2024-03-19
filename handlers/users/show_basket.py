from aiogram import types
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from models import Orders, Users
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from states.main_states import Main
from .products import generate_cart_message, create_basket_keyboard
from utils.db_api.database import Session
from keyboards.default.main_menu import menu_ru 
from sqlalchemy import func


@dp.message_handler(text='🛒 Корзина', state=Main.main_menu)
async def showBasketUser(message: types.Message, state: FSMContext):
    cart_msg = await generate_cart_message(message.from_user.id)
    if cart_msg:
        keyboard_buttons = await create_basket_keyboard(message.from_user.id)
        await message.answer(cart_msg, reply_markup=keyboard_buttons)
        await Main.main_menu.set()
    else:
        await message.answer("Ваша корзина пуста!")
        await message.answer('🏡 Главное меню', reply_markup=menu_ru)
        await Main.main_menu.set()




def get_orders_by_status(user_id, status):
    db = Session()
    # Query the database to retrieve orders
    orders = db.query(Orders).join(Orders.user).filter(Users.telegram_id == user_id, Orders.status == status).all()
    unique_orders = {order.order_number: order for order in orders}.values()

    return unique_orders



# Format the orders data into a message
def format_orders_message(orders):


    db = Session()
    if not orders:
        return "No orders found with the specified status."
    message = "<b>Ваши заказы</b>\n"
    counter = 1

    for order in orders:
        order_nums = order.order_number
        # Query the database to get the total price sum for the specific order number
        total_sum = db.query(func.sum(Orders.total_price)).filter(Orders.order_number == order_nums).scalar()
        total_sum = total_sum or 0  # If total_sum is None, set it to 0
        message += f"{counter}) <b>Заказ:</b> {str(order.order_number)} - Итоговая цена: {total_sum:.0f}-сум\n"

        counter += 1

    return message


@dp.message_handler(text='📦 Мои заказы', state=Main.main_menu)
async def showFinishedOrders(message: types.Message, state: FSMContext):
    db = Session()
    orders = get_orders_by_status(message.from_user.id, 'qabul')

    # Format orders into a message
    xabar = format_orders_message(orders)
    await message.answer(xabar)

    # Send the message to the user via the bot
 


    db.close()