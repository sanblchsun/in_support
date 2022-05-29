import re
import emoji
from aiogram import types
from aiogram.dispatcher import FSMContext
from states.state_form import Form
from loader import dp, bot
from base.sqlighter import SQLighter
from mail.send_mail import send_email_with_attachment
from keyboards.inline.buttons import attach_yes_no, send_request_yes_no, request_delete_with_data, reject_request, \
    save_person_data


@dp.message_handler(state=Form.full_name, content_types=types.ContentType.TEXT)
async def action_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Укажите Ваш контактный телефон:")
    await state.set_state(Form.telefon)


@dp.message_handler(state=Form.telefon, content_types=types.ContentType.TEXT)
async def action_telefon(message: types.Message, state: FSMContext):
    await state.update_data(telefon=message.text)
    await message.answer("Укажите Ваш e-mail:")
    await state.set_state(Form.e_mail)


@dp.message_handler(state=Form.e_mail, content_types=types.ContentType.TEXT)
async def action_e_mail(message: types.Message, state: FSMContext):
    if not bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", message.text)):
        await message.answer('Недействительный email ✉. Повторите')
        return

    await state.update_data(e_mail=message.text)
    await message.answer("От какой компании обращаетесь:")
    await state.set_state(Form.firma)


@dp.message_handler(state=Form.firma, content_types=types.ContentType.TEXT)
async def action_insert_in_base(message: types.Message, state: FSMContext):
    await state.update_data(firma=message.text)
    keyboard = save_person_data()
    await message.answer('Сохранить выше введенную информацию, чтобы использовать в следующей заявке\n'
                         'Нажимая на кнопку ДА, вы даете согласие на обработку ваших персональных данных',
                         reply_markup=keyboard)


@dp.message_handler(state=Form.description, content_types=['text'])
async def action_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    keyboard = attach_yes_no()
    await message.answer(emoji.emojize(':linked_paperclips:') +
                         'Хотите приложить файлы и фотографии?', reply_markup=keyboard)


@dp.message_handler(state=Form.attach, content_types=['document'])
async def action_document(message: types.Message, state: FSMContext):
    await message.answer(f'Обработан файл: {message.document.file_name}')
    url_file = await message.document.get_url()
    async with state.proxy() as data:
        data['dist_url_and_namefile'][url_file] = (message.from_user.id, message.message_id, message.document.file_name)


@dp.message_handler(state=Form.attach, content_types=['photo'])
async def action_photo(message: types.Message, state: FSMContext):
    url_file = await message.photo[-1].get_url()
    file_name = str(url_file).split('/')[-1]
    await message.answer(f'Обработан файл: {file_name}')
    async with state.proxy() as data:
        data['dist_url_and_namefile'][url_file] = (message.from_user.id, message.message_id, file_name)


@dp.message_handler(state=Form.attach, commands=['attach'])
async def end_form(message: types.Message, state: FSMContext):
    keyboard = send_request_yes_no()
    await message.answer(emoji.emojize(':envelope:  Заявка готова, отправить?'),
                         reply_markup=keyboard)
    await state.set_state(Form.send_request)


@dp.callback_query_handler(lambda c: c.data == "create_request", state='*')
async def action_del_user_data(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    keyboard = reject_request()
    await callback_query.message.edit_text(
        emoji.emojize(':warning:  НАЧАЛО ФОРМЫ ЗАЯВКИ  :down_arrow: :down_arrow: :down_arrow:\n\n'),
        reply_markup=keyboard)
    await callback_query.message.answer("Укажите Ваши фамилию и имя:")
    await state.set_state(Form.full_name)


@dp.callback_query_handler(lambda c: c.data == "del_user_data", state='*')
async def action_del_user_data(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    sql_object = SQLighter("base/db.db")
    sql_object.delete_user_data(callback_query.from_user.id)
    await callback_query.message.edit_text(
        emoji.emojize(':warning:  НАЧАЛО ФОРМЫ ЗАЯВКИ  :down_arrow: :down_arrow: :down_arrow:\n\n'))
    await callback_query.message.answer("Вы отменили заявку")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "reject_request", state='*')
async def action_del_user_data(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text(
        emoji.emojize(':warning:  НАЧАЛО ФОРМЫ ЗАЯВКИ  :down_arrow: :down_arrow: :down_arrow:\n\n'))
    await callback_query.message.answer("Вы отменили заявку")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "del_current_request", state='*')
async def action_del_user_data(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text("Вы отменили заявку")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "attach_yes", state='*')
async def action_request_to_support1(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Form:description':
        await bot.answer_callback_query(callback_query_id=callback_query.id)
        await callback_query.message.edit_text(emoji.emojize(':linked_paperclips:') +
                                               "   без  текста вложите файлы или сделайте фотограции\n"
                                               "после нажмите на ссылку /attach")
        await state.set_state(Form.attach)
    else:
        await callback_query.message.edit_text("---------")


@dp.callback_query_handler(lambda c: c.data == "attach_no", state='*')
async def action_request_to_support2(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Form:description':
        await bot.answer_callback_query(callback_query_id=callback_query.id)
        keyboard = send_request_yes_no()
        await callback_query.message.edit_text(emoji.emojize(":envelope: отправить заявку?"), reply_markup=keyboard)
        await state.set_state(Form.send_request)
    else:
        await callback_query.message.edit_text("---------")


@dp.callback_query_handler(lambda c: c.data == "send_yes", state=Form.send_request)
async def action_request_to_support(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(send_yes_no=True)
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    data = await state.get_data()
    dist_url_and_namefile = data.get('dist_url_and_namefile')
    await callback_query.message.edit_text("Вы нажали 'Отправить сообщение'")
    message_id = bot.id
    await send_email_with_attachment(full_name=data.get('full_name'),
                                     e_mail=data.get('e_mail'),
                                     firma=data.get('firma'),
                                     cont_telefon=data.get('telefon'),
                                     description=data.get('description'),
                                     message_id=message_id,
                                     http_to_attach=dist_url_and_namefile)
    await callback_query.message.edit_text("Ваша заявка отправлена. "
                                           "\nЧтобы направить еще одну заявку, нажмите Меню->start")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "send_no", state=Form.send_request)
async def action_request_to_support(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(send_yes_no=True)
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text("Вы передумали отправлять запрос, что бы создать заявку нажмите /start")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "save_no", state='*')
async def action_request_to_support2(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    await callback_query.message.edit_text(emoji.emojize("Отказ от сохранения.\n\n"
                                                         ":page_facing_up: Расскажите - что у вас случилось?"))
    await state.set_state(Form.description)


@dp.callback_query_handler(lambda c: c.data == "save_yes", state='*')
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
    await state.set_state(Form.description)
    await callback_query.message.edit_text(emoji.emojize("Сохранены. \n\n"
                                                         ":page_facing_up: Расскажите - что у вас случилось?"))
