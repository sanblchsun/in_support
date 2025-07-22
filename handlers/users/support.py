import asyncio
import re

import emoji
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageError

from keyboards.default.buttons import send_request_yes_no_def
# 1c integrated
from module1c.action import get_status
# 1c integrated
from .html import get_html
from mail.send_mail import send_email_with_attachment
from states.state_form import Form
from loader import dp, bot
from base.sqlighter import SQLighter
from keyboards.inline.buttons import *
from utils.notify_admins import send_messege_to_chat, is_admin_get_firms
from module1c import action
from bs4 import BeautifulSoup
from .message_del import msg_delete


@dp.message_handler(state=None, commands=['firms'])
async def action_firm(message: types.Message, state: FSMContext):
    usr_id = message.from_user.id
    usr_id_str = str(usr_id)
    res_fo_if = is_admin_get_firms(usr_id_str)
    if res_fo_if:
        await message.answer(f"Уже есть такой список фирм для уведомления: {res_fo_if}. \n"
                             f"Ваши старые записи будут стерты")
        await state.set_state(Form.update_for_firm)
    else:
        await state.set_state(Form.add_for_firm)

    await message.answer("Введите через запятую слова, входящее в название фирм")


@dp.message_handler(state=Form.add_for_firm, content_types=types.ContentType.TEXT)
async def action_for_firm(message: types.Message, state: FSMContext):
    list_firm = message.text
    sql_object = SQLighter("base/db.db")
    sql_object.add_admin(message.from_user.id, list_firm)
    await message.answer(f"Вы ввели: {list_firm}\n  данные записаны")
    await state.finish()


@dp.message_handler(state=Form.update_for_firm, content_types=types.ContentType.TEXT)
async def action_for_firm(message: types.Message, state: FSMContext):
    list_firm = message.text
    sql_object = SQLighter("base/db.db")
    sql_object.update_admin(message.from_user.id, list_firm)
    await message.answer(f"Вы ввели: {list_firm}\n данные записаны")
    await state.finish()


@dp.message_handler(state=None, commands=["unsubscribe"])
async def action_unsubscribe(message: types.Message, state: FSMContext):
    usr_id = message.from_user.id
    usr_id_str = str(usr_id)
    res_fo_if = is_admin_get_firms(usr_id_str)
    if res_fo_if:
        sql_object = SQLighter("base/db.db")
        sql_object.del_subscriptions_for_admin(usr_id_str)
        await message.answer("Вы отписались от всех уведомлений")
    else:
        await message.answer("У вас нет подписки на уведомления")


@dp.message_handler(state=Form.full_name, content_types=types.ContentType.TEXT)
async def action_full_name(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("""Разрешено не больше 100 знаков.
        Введите пожалуйста Ваши фамилию и имя:""")
        return
    await state.update_data(full_name=message.text)
    await message.answer("Укажите Ваш контактный телефон:")
    await state.set_state(Form.telefon)


@dp.message_handler(state=Form.telefon, content_types=types.ContentType.TEXT)
async def action_telefon(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Введите не боллее 50 знаков для телефона")
        return
    await state.update_data(telefon=message.text)
    await message.answer("Укажите Ваш e-mail:")
    await state.set_state(Form.e_mail)


@dp.message_handler(state=Form.e_mail, content_types=types.ContentType.TEXT)
async def action_e_mail(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("""Разрешено не больше 100 знаков.
        Введите пожалуйста Ваш e-mail:""")
        return
    if not bool(re.search(r"^[\w\.\+\-]+\@[\w\.\-]+\.[a-z]{2,7}$", message.text)):
        await message.answer('Недействительный email ✉. Повторите')
        return

    await state.update_data(e_mail=message.text)
    await message.answer("От какой компании обращаетесь:")
    await state.set_state(Form.firma)


@dp.message_handler(state=Form.firma, content_types=types.ContentType.TEXT)
async def action_insert_in_base(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("""Разрешено не больше 100 знаков.
        От какой компании обращаетесь:""")
        return
    await state.update_data(firma=message.text)
    keyboard = save_person_data()
    await message.answer("""Я могу сохранить Ваши данные, чтобы в следующий раз их не нужно было вводить при
отправке заявки. Нажимая кнопку «ДА», Вы даете согласие на обработку Ваших
персональных данных.""",
                         reply_markup=keyboard)


@dp.message_handler(state=Form.description, content_types=['text'])
async def action_description(message: types.Message, state: FSMContext):
    await msg_delete(state, message.from_user.id, message.message_id)
    html = get_html(description=message.text)
    data = await state.get_data()
    try:
        await bot.edit_message_text(text=f"""{html}""",
                                    chat_id=message.from_user.id,
                                    message_id=data.get("message_for_edit"),
                                    reply_markup=None)
    except MessageError as e: ...
    await state.update_data(description=message.text)
    try:
        await message.delete()
    except MessageError as e:
        ...
    keyword = buttons_priority()
    await message.answer("Укажите приоритет заявки:", reply_markup=keyword)
    await state.set_state(Form.priority)


@dp.callback_query_handler(lambda c: c.data in ["low_btn_press",
                                                "medium_btn_press",
                                                "high_btn_press",
                                                "critical_btn_press"],
                           state=Form.states_names)
async def action_priority_btn(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    if callback_query.data == "low_btn_press":
        await state.update_data(priority="Низкий")
    elif callback_query.data == "medium_btn_press":
        await state.update_data(priority="Средний")
    elif callback_query.data == "high_btn_press":
        await state.update_data(priority="Высокий")
    else:
        await state.update_data(priority="Критический")
    data = await state.get_data()
    html_request = get_html(description=data.get('description'), priority=data.get('priority'))
    try:
        await bot.edit_message_text(text=html_request,
                                    chat_id=callback_query.from_user.id,
                                    message_id=data.get('message_for_edit'))
    except Exception as e:
        await state.finish()
        await callback_query.answer("""Была удалена форма заявки в истории вашего телеграмм, 
        начните сначала, нажав /cancel потом /start""")
    keyboard = attach_yes_no()
    msg = await callback_query.message.answer(emoji.emojize(':linked_paperclips:') +
                                              'Хотите приложить файлы и фотографии?', reply_markup=keyboard)
    await msg_delete(state, callback_query.from_user.id, msg.message_id)
    await state.set_state(Form.attach)


@dp.callback_query_handler(lambda c: c.data == "create_request", state=Form.beginning)
async def action_del_user_data(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text("Укажите Ваши фамилию и имя:")
    await state.set_state(Form.full_name)


@dp.callback_query_handler(lambda c: c.data == "attach_yes", state=Form.attach)
async def action_request_to_support1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text(emoji.emojize(':linked_paperclips:') +
                                           "   вложите файл или сделайте фотографию")
    await state.set_state(Form.attach_yes)


@dp.callback_query_handler(lambda c: c.data == "attach_no", state=Form.attach)
async def action_request_to_support2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    keyboard = send_request_yes_no_def()
    msg = await callback_query.message.answer(emoji.emojize(":envelope: отправить заявку?"),
                                              reply_markup=keyboard)
    await msg_delete(state, callback_query.from_user.id, msg.message_id)
    await state.set_state(Form.send_request)


@dp.message_handler(text="Отправить заявку \U0001FAE1", state=Form.send_request)
async def action_request_to_support(message: types.Message, state: FSMContext):
    async def edit_html_request(num):
        data = await state.get_data()
        html_request = get_html(description=data.get('description'),
                                priority=data.get('priority'),
                                number_request=num)
        try:
            # 1c integrated
            # await bot.edit_message_text(text=html_request,
            #                             chat_id=message.from_user.id,
            #                             message_id=data.get('message_for_edit'), reply_markup=btn_get_status())
            # 1c integrated

            await bot.edit_message_text(text=html_request,
                                        chat_id=message.from_user.id,
                                        message_id=data.get('message_for_edit'))


        except Exception as e:
            await state.finish()
            await message.answer("Была удалена форма заявки в истории вашего телеграмм, начните сначала")

    await state.update_data(send_yes_no=True)
    data = await state.get_data()
    dist_url_and_namefile = data.get('dist_url_and_namefile')
    await msg_delete(state, message.from_user.id, message.message_id)
    msg = await message.answer("Вы нажали 'Отправить заявку'", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except MessageError as e:
        ...
    # 1c integrated
    number_from_1c = await action.set_brom(full_name=data.get('full_name'),
                                           e_mail=data.get('e_mail'),
                                           firma=data.get('firma'),
                                           cont_telefon=data.get('telefon'),
                                           description=data.get('description'),
                                           priority=data.get('priority'))
    user_id = message.from_user.id
    # 1c integrated
    ident_error, check_send_bot = await send_email_with_attachment(full_name=data.get('full_name'),
                                                                   e_mail=data.get('e_mail'),
                                                                   firma=data.get('firma'),
                                                                   cont_telefon=data.get('telefon'),
                                                                   description=data.get('description'),
                                                                   priority=data.get('priority'),
                                                                   message_id=user_id,
                                                                   http_to_attach=dist_url_and_namefile,
                                                                   number_from_1c=number_from_1c)
    if ident_error:
        await message.edit_text(
            f"Ошибка при отправке заявки: {ident_error}. "
            f"Что то пошло не так, обратитесь к поставщику продукта"
        )
    else:
        await message.answer(f"""Заявка отправлена, 
    номер заявки: {number_from_1c}.
    Чтобы направить еще одну заявку, нажмите /start""")
        # 1c integrated
        await edit_html_request(number_from_1c)
        # 1c integrated

        if check_send_bot:
            await send_messege_to_chat(dp,
                                       full_name=data.get('full_name'),
                                       e_mail=data.get('e_mail'),
                                       firma=data.get('firma'),
                                       cont_telefon=data.get('telefon'),
                                       description=data.get('description'),
                                       priority=data.get('priority'),
                                       number_from_1c=number_from_1c)

    await state.finish()

# 1c integrated
# @dp.callback_query_handler(lambda c: c.data == "btn_get_status", state=None)
# async def action_btn_get_status(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query_id=callback_query.id)
#     msg_html = callback_query.message.parse_entities()
#     soup = BeautifulSoup(msg_html, 'html.parser')
#     num = soup.findAll("code")[3].string
#     status = await get_status(num)
#     tag = soup.findAll("code")[2]
#     tag.string = status
#     html_request = str(soup)
#     try:
#         await bot.edit_message_text(text=html_request,
#                                     chat_id=callback_query.from_user.id,
#                                     message_id=callback_query.message.message_id, reply_markup=btn_get_status())
#     except Exception as e:
#         await state.finish()
#         await callback_query.answer("Была удалена форма заявки в истории вашего телеграмм, начните сначала")
# 1c integrated

# @dp.callback_query_handler(lambda c: c.data == "save_no", state=Form.states_names)
# async def action_request_to_support2(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query_id=callback_query.id)
#     await callback_query.message.edit_text(emoji.emojize("Отказ от сохранения."))
#     await state.finish()


@dp.callback_query_handler(lambda c: c.data == "save_yes", state=Form.states_names)
async def action_request_to_support2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    sql_object = SQLighter("base/db.db")
    current_state = await state.get_data()

    sql_object.add_user(
        callback_query.from_user.id,
        current_state['full_name'],
        current_state['telefon'],
        current_state['e_mail'],
        current_state['firma'], )
    await state.finish()
    await callback_query.message.answer("""Спасибо, Ваши данные сохранены и 
будут автоматически использоваться при подаче всех
последующих заявок. Нажмите /start, чтобы отправить заявку.""")
