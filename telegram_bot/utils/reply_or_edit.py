from telegram import Update

def reply_or_edit(update: Update, text: str, reply_markup=None, parse_mode=None):
    """
    Универсальная функция для ответа пользователю:
    - если это обычное сообщение — reply
    - если это callback (нажатие на inline-кнопку) — edit
    """
    if update.callback_query:
        try:
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception:
            update.callback_query.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
    elif update.message:
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
