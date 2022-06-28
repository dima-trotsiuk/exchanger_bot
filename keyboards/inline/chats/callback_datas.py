from aiogram.utils.callback_data import CallbackData

chats_button_callback = CallbackData("chats_button", "type_command", "action")
select_update_group_buttons_callback = CallbackData("select_update_group_buttons", "type_command", "pk_group", "pk_chat")
