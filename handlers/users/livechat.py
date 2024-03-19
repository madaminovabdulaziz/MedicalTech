from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from states.main_states import Main
from keyboards.default.main_menu import menu_ru 



def answer(user_chat_id):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.insert(InlineKeyboardButton(text="Javob berish", callback_data=f'answer:{user_chat_id}'))
    return btn



@dp.message_handler(text='📝 Связаться с нами', state=Main.main_menu)
async def startLiveChat(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, задайте свой вопрос, и мы ответим в ближайшее время.")
    await state.set_state("get_questions")



@dp.message_handler(state="get_questions")
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    # Forward user's message to the admin group
    question = f"""
❗️ Yangi savol:
From: @{message.from_user.username}

Savol:
{message.text}
"""
    

    await bot.send_message(chat_id='5069131343', text=question, reply_markup=answer(user_id))


    await message.answer("Ваше сообщение было отправлено в нашу службу поддержки. Мы ответим в ближайшее время")
    await message.answer('🏡 Главное меню', reply_markup=menu_ru)
    await Main.main_menu.set()




@dp.callback_query_handler(text_contains='answer',state="*")
async def answer_to_question(call: CallbackQuery, state: FSMContext):
    data = call.data.rsplit(":")
    user_id = data[1]
    await state.update_data({"chat_id": user_id})
    await call.message.answer("Javob yozing: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state('get_from_user')
    

@dp.message_handler(state='get_from_user')
async def send_answer(message: Message, state: FSMContext):
    admin_answer = f"""
<b>Админ ответил:</b>
{message.text}

"""
    data = await state.get_data()
    user_id = data.get('chat_id')
    await bot.send_message(chat_id=user_id, text=admin_answer)
    await message.answer('Javobingiz muvaffaqiyatli yuborildi!')
    await message.answer('🏡 Главное меню', reply_markup=menu_ru)
    await Main.main_menu.set()



