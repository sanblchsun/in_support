
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from base.sqlighter import SQLighter
from loader import dp
from aiogram.dispatcher import FSMContext
from states.state_form import Form
from keyboards.inline.buttons import request_delete_with_data, request_or_reject


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dist_url_and_namefile'] = {}
        data['list_photo_path'] = []
        data['send_yes_no'] = True

    sql_object = SQLighter('base/db.db')
    list_data_client = sql_object.get_client(message.from_user.id)
    if bool(len(list_data_client)):
        keyboard = request_delete_with_data()
        await message.answer(f"Привет, {message.from_user.full_name}! Ваши данные для автозаполнения формы заявки:.\n \n"
                             f"ФИО: {list_data_client[0][1]}\n "
                             f"Организация: {list_data_client[0][2]}\n"
                             f"e-mail: {list_data_client[0][3]}\n"
                             f"телефон: {list_data_client[0][4]}\n\n"
                             f"Введите описание ваше обращение в техподдержку",
                             reply_markup=keyboard)
        await state.set_state(Form.description)
        await state.update_data(full_name=list_data_client[0][1])
        await state.update_data(firma=list_data_client[0][2])
        await state.update_data(e_mail=list_data_client[0][3])
        await state.update_data(telefon=list_data_client[0][4])
    else:
        keyboard = request_or_reject()
        await message.answer(f"Привет, {message.from_user.full_name}!"
                             f" \n Вам будет предложено сохранить часть информации, что бы не заполнять ее снова ",
                             reply_markup=keyboard)
        await state.set_state(Form.beginning)


