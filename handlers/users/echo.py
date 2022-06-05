from states.state_form import Form

from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None, content_types=types.ContentTypes.ANY)
async def bot_echo(message: types.Message):
    await message.answer('Что бы заполнить и отправить заявку нажмите на ссылку /start')


# Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state_current = await state.get_state()
    if state_current == 'Form:full_name':
        await message.answer('Введите ваше Имя и Фамилию')
    elif state_current == 'Form:telefon':
        await message.answer('Введите ваш телефон')
    elif state_current == 'Form:e_mail':
        await message.answer('Введите ваш e-mail')
    elif state_current == 'Form:firma':
        await message.answer('Нажмите кнопку')
    elif state_current == 'Form:beginning':
        await message.answer('Нажмите кнопку')
    elif state_current == 'Form:priority':
        await message.answer("Нажмите на кнопку")
    else:
        await message.answer('Неверный формат')

