from aiogram.utils.exceptions import MessageError

from loader import bot


async def msg_delete(state, message_from_user_id,  message_id):
    data = await state.get_data()
    message_for_edit = data.get("message_for_edit")
    for i in range(int(message_for_edit) + 1, int(message_id)):
        try:
            await bot.delete_message(chat_id=message_from_user_id, message_id=i)
        except MessageError as e: ...
    return message_for_edit