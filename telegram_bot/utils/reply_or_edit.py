def reply_or_edit(update, text, reply_markup=None):
    """
    Универсальная функция для ответа пользователю:
    - если это обычное сообщение - reply
    - если это callback (нажатие на inline-кнопку) - edit
    """
    if update.callback_query:
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text, reply_markup=reply_markup)
