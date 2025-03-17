from aiogram.utils.exceptions import MessageError

from loader import bot


async def msg_delete(state, message_from_user_id,  message_id):
    data = await state.get_data()
    message_for_edit = data.get("message_for_edit")
    try:
        start_int = int(message_for_edit)
        end_int = int(message_id)
    except TypeError:
        return
    for i in range(start_int + 1, end_int):
        try:
            await bot.delete_message(chat_id=message_from_user_id, message_id=i)
        except MessageError as e: ...