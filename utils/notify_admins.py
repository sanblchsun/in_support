import logging
from aiogram import types
from aiogram import Dispatcher
from aiogram.utils.exceptions import ChatNotFound

from base.sqlighter import SQLighter
from data.config import ADMINS

def is_admin_get_firms(usr_id):
    if usr_id in ADMINS:
        sql_object  = SQLighter("base/db.db")
        list_filtr = sql_object.get_admins_firms(usr_id)
        if list_filtr:
            res = list_filtr[0][0].split(",")
            return res
    return False

async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")
        except ChatNotFound as err:
            logging.exception(f'Ошибка!!!!!!!{err}')



async def send_messege_to_admin(dp: Dispatcher,
                                     full_name,
                                     e_mail,
                                     firma,
                                     cont_telefon,
                                     description,
                                     priority):

    # html = '<b>жирный</b>, <strong>жирный</strong>\
    #         <span class="tg-spoiler">скрытый текст</span>, <tg-spoiler>скрытый текст</tg-spoiler>\
    #         <i>курсив</i>, <em>курсив</em>\
    #         <u>подчеркивание</u>, <ins>подчеркивание</ins>\
    #         <s>зачеркнуто</s>, <strike>зачеркнуто</strike>, <del>зачеркнуто</del>\
    #         <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>\
    #         <b>\
    #         bold <i>italic bold <s>italic bold strikethrough\
    #         <span class="tg-spoiler">italic bold strikethrough spoiler</span></s>\
    #         <u>underline italic bold</u></i> bold\
    #         </b>\
    #         <code>встроенный код фиксированной ширины</code>\
    #         <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>\
    #         <pre>\
    #         <code class="language-python">\
    #         предварительно отформатированный блок кода фиксированной ширины,\
    #         написанный на языке программирования Python\
    #         </code>\
    #         </pre>\
    #         <a href="tg://user?id=123456789">встроенное упоминание пользователя</a>\
    #         <pre>предварительно отформатированный блок кода фиксированной ширины</pre>'

    for admin in ADMINS:
        res_for_if = is_admin_get_firms(admin)
        if res_for_if:
            for pattern in res_for_if:
                pattern_tmp = str(pattern).lower().strip()
                firma_tmp = str(firma).lower().strip()
                if pattern_tmp in firma_tmp:
                    html = \
                        f"<i><b>Компания: </b></i>\n<code>{firma}</code>\n" \
                        f"<i><b>Фамилия Имя: </b></i>\n<code>{full_name}</code>\n" \
                        f"<i><b>Контактный телефон: </b>\n</i><code>{cont_telefon}</code>\n" \
                        f"<i><b>E-mail адрес: </b></i>\n<code>{e_mail}</code>\n" \
                        f"<i><b>Описание проблемы: </b></i>\n<code>{description}</code>\n" \
                        f"<i><b>Приоритет заявки: </b></i>\n<code>{priority}</code>\n"

                    await dp.bot.send_message(admin, html, parse_mode=types.ParseMode.HTML)
                    logging.info(f'html: send, pattern_tmp: {pattern_tmp}, firma_tmp: {firma_tmp}, admin: {admin}, ADMINS: {ADMINS}')


